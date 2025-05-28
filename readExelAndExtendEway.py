import os
import pandas as pd
from bs4 import BeautifulSoup
import json
from datetime import datetime
from time import sleep
from datetime import timedelta
import logging
import traceback
import sys

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.firefox.options import Options

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

def setup_logging():
    """
    Setup comprehensive logging configuration
    Creates multiple log files for different purposes
    """
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Generate timestamp for log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Configure main logger
    logger = logging.getLogger('EwayBillAutomation')
    logger.setLevel(logging.DEBUG)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(funcName)-20s | Line:%(lineno)-4d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # 1. DETAILED DEBUG LOG (Everything)
    debug_handler = logging.FileHandler(f'{log_dir}/debug_{timestamp}.log', encoding='utf-8')
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(detailed_formatter)
    logger.addHandler(debug_handler)
    
    # 2. ERROR LOG (Errors only)
    error_handler = logging.FileHandler(f'{log_dir}/errors_{timestamp}.log', encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    # 3. OPERATIONS LOG (Main operations)
    operations_handler = logging.FileHandler(f'{log_dir}/operations_{timestamp}.log', encoding='utf-8')
    operations_handler.setLevel(logging.INFO)
    operations_handler.setFormatter(simple_formatter)
    logger.addHandler(operations_handler)
    
    # 4. CONSOLE OUTPUT (User-friendly)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    return logger

# Initialize logger
logger = setup_logging()

# ============================================================================
# CUSTOM DECORATORS FOR LOGGING
# ============================================================================

def log_function_call(func):
    """Decorator to log function entry and exit"""
    def wrapper(*args, **kwargs):
        logger.debug(f"🔵 ENTERING: {func.__name__} with args: {args[1:] if len(args) > 1 else 'None'}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"🟢 EXITING: {func.__name__} - SUCCESS")
            return result
        except Exception as e:
            logger.error(f"🔴 EXITING: {func.__name__} - FAILED: {str(e)}")
            logger.error(f"📋 TRACEBACK: {traceback.format_exc()}")
            raise
    return wrapper

def log_selenium_action(action_name):
    """Decorator to log selenium actions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.debug(f"🤖 SELENIUM ACTION: {action_name}")
            try:
                result = func(*args, **kwargs)
                logger.debug(f"✅ SELENIUM SUCCESS: {action_name}")
                return result
            except Exception as e:
                logger.error(f"❌ SELENIUM FAILED: {action_name} - {str(e)}")
                # Log current URL and page source for debugging
                if hasattr(args[0], 'driver'):
                    try:
                        logger.debug(f"🌐 CURRENT URL: {args[0].driver.current_url}")
                        logger.debug(f"📄 PAGE TITLE: {args[0].driver.title}")
                    except:
                        pass
                raise
        return wrapper
    return decorator

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

@log_function_call
def read_user_credentials(file_path):
    """Read user credentials from JSON file"""
    logger.info(f"📖 Reading credentials from: {file_path}")
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        user_name = data['user_name']
        password = data['password']
        logger.info(f"✅ Credentials loaded for user: {user_name}")
        return user_name, password
    except FileNotFoundError:
        logger.error(f"❌ Credentials file not found: {file_path}")
        raise
    except KeyError as e:
        logger.error(f"❌ Missing credential field: {e}")
        raise

@log_function_call
def read_eway_csv(file_path):
    """Read eway bill data from CSV file"""
    logger.info(f"📖 Reading eway data from: {file_path}")
    eway_list = []
    try:
        df = pd.read_csv(file_path, dtype=str)
        eway_list = df.to_dict(orient='records')
        logger.info(f"✅ Loaded {len(eway_list)} eway bills from CSV")
        logger.debug(f"📋 CSV columns: {list(df.columns)}")
        return eway_list
    except FileNotFoundError:
        logger.error(f"❌ CSV file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"❌ Error reading CSV: {str(e)}")
        raise

@log_function_call
def filter_eway_by_valid_until(eway_list):
    """Filter eway bills that expire today"""
    logger.info("🔍 Filtering eway bills expiring today...")
    
    current_date = datetime.now()
    current_time = current_date.time()
    logger.debug(f"⏰ Current datetime: {current_date}")
    
    # If current time is between 00:00:00 and 08:00:00, consider the previous date
    if datetime.strptime("00:00:00", "%H:%M:%S").time() <= current_time and current_time < datetime.strptime("08:00:00", "%H:%M:%S").time():
        current_date = current_date - timedelta(days=1)
        logger.info("🌅 Early morning detected, using previous date for filtering")
    
    current_date_str = current_date.strftime("%d/%m/%Y")
    logger.info(f"📅 Target expiry date: {current_date_str}")
    
    eway_about_to_expire = [eway for eway in eway_list if eway.get("Valid Untill") == current_date_str]
    
    logger.info(f"🎯 Found {len(eway_about_to_expire)} eway bills expiring on {current_date_str}")
    
    # Log each eway bill found
    for i, eway in enumerate(eway_about_to_expire, 1):
        logger.debug(f"📦 {i}. EWB No: {eway.get('EWB.No', 'N/A')} - Valid Until: {eway.get('Valid Untill', 'N/A')}")
    
    return eway_about_to_expire

# ============================================================================
# MAIN SCRIPT INITIALIZATION
# ============================================================================

# WELCOME MESSAGES
print("=" * 80)
print("🚀 WELCOME TO EWAY BILL EXTENSION SCRIPT BY SHUBHAM MALIK")
print("=" * 80)
logger.info("🚀 Starting Eway Bill Extension Script")
logger.info("📋 Script will extend eway bills expiring today")
logger.info("⏰ Recommended run time: 08:00:00 to 16:00:00")

# Load credentials
file_path = './user.json'
try:
    user_name, password = read_user_credentials(file_path)
    logger.info(f"👤 User authenticated: {user_name}")
except Exception as e:
    logger.error("🚫 Failed to load credentials, exiting...")
    sys.exit(1)

# Load eway data
eway_file_path = './eway.csv'
try:
    eway_list = read_eway_csv(eway_file_path)
except Exception as e:
    logger.error("🚫 Failed to load eway data, exiting...")
    sys.exit(1)

# Filter expiring eway bills
eway_about_to_expire = filter_eway_by_valid_until(eway_list)
if not eway_about_to_expire:
    logger.warning("⚠️ No eway bills found expiring today")
    print("No eway bills to process. Exiting...")
    sys.exit(0)

# ============================================================================
# MAIN CLASS
# ============================================================================

class extendEwayBill:
    def __init__(self):
        logger.info("🔧 Initializing Eway Bill Extension System")
        
        self.login_url = "https://ewaybillgst.gov.in/Login.aspx"
        self.txt_username = user_name
        self.txt_password = password

        # Clean up old log files
        self.cleanup_old_files()

        self.list_eway_cum_vehicle = eway_about_to_expire
        
        # Configure Firefox options
        firefox_options = Options()
        # firefox_options.add_argument("--headless")  # Uncomment for headless mode
        logger.debug("🦊 Configuring Firefox browser")
        
        try:
            self.driver = webdriver.Firefox(options=firefox_options)
            self.wait = WebDriverWait(self.driver, 10)
            logger.info("✅ Browser initialized successfully")
            
            # Set window size for better visibility
            self.driver.maximize_window()
            logger.debug("🖥️ Browser window maximized")
            
            # Execute main workflow
            self.execute_main_workflow()
            
        except Exception as e:
            logger.error(f"🚫 Critical error during execution: {str(e)}")
            logger.error(f"📋 Full traceback: {traceback.format_exc()}")
            raise
        finally:
            if hasattr(self, 'driver'):
                self.driver.quit()
                logger.info("🔚 Browser session closed")

    @log_function_call
    def cleanup_old_files(self):
        """Clean up old log files"""
        log_file = "log.txt"
        eway_file = "eway.txt"
        
        for file in [log_file, eway_file]:
            if os.path.exists(file):
                os.remove(file)
                logger.debug(f"🗑️ Removed old file: {file}")

    @log_function_call
    def execute_main_workflow(self):
        """Execute the main workflow"""
        logger.info("🔄 Starting main workflow execution")
        
        try:
            # STEP 1: Login once and get vehicle details
            logger.info("📋 STEP 1: Login and getting vehicle details for all eway bills")
            self.fresh_login("Getting Vehicle Details")
            self.list_eway_cum_vehicle = self.getPrintEwayAndFindCurrentVehicle() 
            self.write_eway_to_file()
            
            # STEP 2: Use same session to extend eway bills
            logger.info("🔄 STEP 2: Extending eway bills using existing session")
            self.extendEwayBills()
            
            logger.info("🎉 Main workflow completed successfully")
            
        except Exception as e:
            logger.error(f"🚫 Main workflow failed: {str(e)}")
            raise

    @log_selenium_action("Fresh Login")
    def fresh_login(self, operation_name=""):
        """Perform fresh login for each major operation to avoid CSRF token errors"""
        logger.info(f"🔐 FRESH LOGIN FOR: {operation_name}")
        
        try:
            # Navigate to login page
            logger.debug("🌐 Navigating to login page...")
            self.driver.get(self.login_url)
            logger.debug(f"📍 Current URL: {self.driver.current_url}")
            
            # Handle any initial alerts and modals
            self.handle_all_popups()
            
            # FIRST LOGIN ATTEMPT
            logger.debug("🔑 First login attempt...")
            txt_username = self.wait.until(EC.presence_of_element_located((By.ID, "txt_username")))
            txt_username.clear()
            txt_username.send_keys(self.txt_username)
            logger.debug("👤 Username entered")

            txt_password = self.driver.find_element(By.ID, "txt_password")
            txt_password.clear()
            txt_password.send_keys(self.txt_password)
            logger.debug("🔒 Password entered")

            # REFRESH THE PAGE TO AVOID CSRF TOKEN ERROR
            logger.debug("🔄 Refreshing page to reset CSRF token...")
            self.driver.refresh()
            sleep(2)

            # RE-ENTER CREDENTIALS AFTER REFRESH (SECOND ATTEMPT)
            logger.debug("🔑 Second login attempt after refresh...")
            txt_username = self.wait.until(EC.presence_of_element_located((By.ID, "txt_username")))
            txt_username.clear()
            txt_username.send_keys(self.txt_username)
            sleep(1)
            logger.debug("👤 Username re-entered")

            txt_password = self.driver.find_element(By.ID, "txt_password")
            txt_password.clear()
            txt_password.send_keys(self.txt_password)
            logger.debug("🔒 Password re-entered")

            # Wait for login to complete
            logger.debug("⏳ Waiting for login to complete...")
            current_url = 'https://ewaybillgst.gov.in/Login.aspx'
            max_attempts = 30
            attempts = 0
            
            while current_url == 'https://ewaybillgst.gov.in/Login.aspx' and attempts < max_attempts:
                try:
                    current_url = self.driver.current_url
                    self.handle_all_popups()
                    sleep(1)
                    attempts += 1
                    
                    if attempts % 5 == 0:  # Log every 5 attempts
                        logger.debug(f"⏳ Login attempt {attempts}/{max_attempts}")
                        
                except UnexpectedAlertPresentException:
                    logger.debug("🚨 Unexpected alert during login")
                    self.handle_all_popups()
                    continue
            
            if attempts >= max_attempts:
                logger.error("🚫 Login timeout - maximum attempts reached")
                return False
            
            # Navigate to main menu
            target_url = "https://ewaybillgst.gov.in/MainMenu.aspx"
            attempts = 0
            
            logger.debug("🏠 Navigating to main menu...")
            while attempts < max_attempts:
                try:
                    current_url = self.driver.current_url
                    logger.debug(f"📍 Current URL: {current_url}")
                    
                    self.handle_all_popups()
                    
                    if current_url != target_url:
                        self.driver.get(target_url)
                        sleep(2)
                        self.handle_all_popups()
                    else:
                        break
                        
                    attempts += 1
                    
                except UnexpectedAlertPresentException:
                    logger.debug("🚨 Alert during navigation")
                    self.handle_all_popups()
                    continue
                except Exception as e:
                    logger.warning(f"⚠️ Navigation error: {str(e)}")
                    attempts += 1
                    continue

            logger.info(f"✅ Successfully logged in for: {operation_name}")
            return True
            
        except Exception as e:
            logger.error(f"🚫 Login failed for {operation_name}: {str(e)}")
            return False

    @log_selenium_action("Handle Alerts")
    def handle_alerts(self):
        """Handle any unexpected alert dialogs"""
        try:
            alert = self.driver.switch_to.alert
            alert_text = alert.text
            logger.debug(f"🚨 Browser Alert detected: {alert_text}")
            alert.accept()
            return True
        except:
            return False
    
    @log_selenium_action("Handle Modals")
    def handle_modals(self):
        """Handle Bootstrap modal dialogs"""
        try:
            modal_selectors = [
                "button[data-dismiss='modal']",
                ".btn-primary[data-dismiss='modal']", 
                ".modal-footer .btn-primary",
                ".close[data-dismiss='modal']",
                "//button[text()='Okay']",
                "//button[text()='OK']",
                "//button[contains(@class, 'btn-primary') and contains(text(), 'Okay')]"
            ]
            
            for selector in modal_selectors:
                try:
                    if selector.startswith("//"):
                        modal_button = self.driver.find_element(By.XPATH, selector)
                    else:
                        modal_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                    
                    if modal_button.is_displayed() and modal_button.is_enabled():
                        modal_button.click()
                        logger.debug(f"✅ Modal closed using selector: {selector}")
                        sleep(1)
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"⚠️ Error handling modals: {str(e)}")
            return False
    
    def handle_all_popups(self):
        """Handle both browser alerts and modal dialogs"""
        handled_alert = self.handle_alerts()
        handled_modal = self.handle_modals()
        return handled_alert or handled_modal

    @log_function_call
    def write_eway_to_file(self):
        """Write eway bill data to file"""
        logger.info("💾 Writing eway bill data to file...")
        try:
            with open("eway.txt", "w") as f:
                for eway in self.list_eway_cum_vehicle:
                    eway_no = eway.get("EWB.No", "UNKNOWN")
                    vehicle_no = eway.get("vehicle_no", "UNKNOWN")
                    f.write(f"{eway_no},{vehicle_no}\n")
                    logger.debug(f"📝 Written: {eway_no},{vehicle_no}")
            logger.info(f"✅ Successfully written {len(self.list_eway_cum_vehicle)} records to eway.txt")
        except Exception as e:
            logger.error(f"❌ Failed to write eway file: {str(e)}")
            raise

    @log_function_call
    def getPrintEwayAndFindCurrentVehicle(self):
        """Get vehicle details for all eway bills"""
        logger.info("🚛 Getting vehicle details for all eway bills...")
        
        total_bills = len(self.list_eway_cum_vehicle)
        logger.info(f"📊 Processing {total_bills} eway bills for vehicle details")
        
        for index, eway_nos_list in enumerate(self.list_eway_cum_vehicle, 1):
            eway_no = eway_nos_list.get("EWB.No", "UNKNOWN")
            logger.info(f"🔍 [{index}/{total_bills}] Processing vehicle details for: {eway_no}")
            
            try:
                link = 'https://ewaybillgst.gov.in/BillGeneration/EBPrint.aspx?cal=1'
                logger.debug(f"🌐 Navigating to: {link}")
                self.driver.get(link)
                
                self.handle_all_popups()
                
                # Fill in eway bill number
                logger.debug(f"📝 Entering eway number: {eway_no}")
                txt_ebillno = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txt_ebillno")))
                txt_ebillno.clear()
                txt_ebillno.send_keys(eway_no)
                
                # Click go button
                btn_go = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_btn_go")
                
                retry_count = 0
                while retry_count < 5:
                    try:
                        btn_go.click()
                        logger.debug("✅ Go Button clicked successfully")
                        break
                    except Exception as e:
                        logger.warning(f"⚠️ Go Button click failed (attempt {retry_count + 1}): {str(e)}")
                        retry_count += 1
                        sleep(1)

                # Get vehicle number and kilometers
                try:
                    logger.debug("🔍 Searching for vehicle details...")
                    ctl00_ContentPlaceHolder1_lblValidFrom = self.wait.until(
                        EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_lblValidFrom"))
                    )
                    ctl00_ContentPlaceHolder1_lblValidFrom_text = ctl00_ContentPlaceHolder1_lblValidFrom.text
                    logger.debug(f"📋 Valid from text: {ctl00_ContentPlaceHolder1_lblValidFrom_text}")
                    
                    # Extract kilometers
                    if '[' in ctl00_ContentPlaceHolder1_lblValidFrom_text and 'Kms' in ctl00_ContentPlaceHolder1_lblValidFrom_text:
                        km_value = int(ctl00_ContentPlaceHolder1_lblValidFrom_text.split('[')[1].split('Kms')[0]) - 2
                        eway_nos_list["kilo_meters"] = km_value
                        logger.info(f"📏 Kilometers extracted: {km_value}")

                    # Get vehicle details from table
                    table = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_GVVehicleDetails")))
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    
                    # Parse table with BeautifulSoup
                    soup = BeautifulSoup(table.get_attribute('outerHTML'), 'html.parser')
                    vehicle_row = soup.find_all('tr')[1]
                    vehicle_column = vehicle_row.find_all('td')[1]
                    vehicle = vehicle_column.text.split('&')[0].strip()
                    
                    eway_nos_list["vehicle_no"] = vehicle
                    logger.info(f"🚛 Vehicle number extracted: {vehicle}")
                    
                except (NoSuchElementException, TimeoutException, IndexError) as e:
                    logger.error(f"❌ Vehicle details not found for {eway_no}: {str(e)}")
                    eway_nos_list["vehicle_no"] = "NOT_FOUND"
                    eway_nos_list["kilo_meters"] = 0
                    continue
                    
            except Exception as e:
                logger.error(f"❌ Error processing eway {eway_no}: {str(e)}")
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
                continue
        
        logger.info("✅ Vehicle details extraction completed")
        return self.list_eway_cum_vehicle

    @log_function_call
    def extendEwayBills(self):
        """Extend each eway bill using existing login session"""
        logger.info("🔄 Starting eway bill extension process using existing session...")
        
        total_bills = len(self.list_eway_cum_vehicle)
        successful_extensions = 0
        failed_extensions = 0
        
        for index, eway_no_vehicle in enumerate(self.list_eway_cum_vehicle, 1):
            eway_no = eway_no_vehicle.get("EWB.No", "UNKNOWN")
            logger.info(f"🔄 [{index}/{total_bills}] Processing extension for: {eway_no}")
            
            try:
                vehicle = eway_no_vehicle.get("vehicle_no")
                kilo_meters = eway_no_vehicle.get("kilo_meters")
                
                # Validate required data
                if not all([eway_no, vehicle, kilo_meters]):
                    logger.error(f"❌ Missing data for {eway_no} - Vehicle: {vehicle}, KM: {kilo_meters}")
                    with open("log.txt", "a") as f:
                        f.write(f"{eway_no},failed - missing data\n")
                    failed_extensions += 1
                    continue
                
                # Extend the eway bill using existing session
                success = self.extend_single_eway(eway_no, vehicle, kilo_meters)
                
                if success:
                    logger.info(f"✅ Extension successful for {eway_no}")
                    with open("log.txt", "a") as f:
                        f.write(f"{eway_no},success\n")
                    successful_extensions += 1
                else:
                    logger.error(f"❌ Extension failed for {eway_no}")
                    with open("log.txt", "a") as f:
                        f.write(f"{eway_no},failed\n")
                    failed_extensions += 1
                        
            except Exception as e:
                logger.error(f"❌ Error extending eway {eway_no}: {str(e)}")
                logger.error(f"📋 Traceback: {traceback.format_exc()}")
                with open("log.txt", "a") as f:
                    f.write(f"{eway_no},error: {str(e)}\n")
                failed_extensions += 1
                continue

        # Final summary
        logger.info("🏁 Extension process completed")
        logger.info(f"📊 SUMMARY: Total: {total_bills}, Successful: {successful_extensions}, Failed: {failed_extensions}")

    @log_selenium_action("Extend Single Eway")
    def extend_single_eway(self, eway_no, vehicle, kilo_meters):
        """Extend a single eway bill"""
        logger.info(f"🔄 Extending eway bill: {eway_no}")
        logger.debug(f"📋 Extension details - Vehicle: {vehicle}, KM: {kilo_meters}")
        
        try:
            # Navigate to extension page
            extension_url = "https://ewaybillgst.gov.in/BillGeneration/EwbExtension.aspx"
            logger.debug(f"🌐 Navigating to: {extension_url}")
            self.driver.get(extension_url)
            self.handle_all_popups()

            # Fill eway number
            logger.debug(f"📝 Entering eway number: {eway_no}")
            eway_input = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txt_no")))
            eway_input.clear()
            eway_input.send_keys(eway_no)
            
            # Click go button
            btn_go = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_Btn_go")
            
            retry_count = 0
            while retry_count < 5:
                try:
                    btn_go.click()
                    logger.debug("✅ Go Button clicked")
                    break
                except:
                    logger.warning(f"⚠️ Go Button click failed (attempt {retry_count + 1})")
                    retry_count += 1
                    sleep(1)

            # Scroll and select radio button
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            logger.debug("📜 Scrolled to bottom")
            
            rbn_extent_0 = self.wait.until(EC.element_to_be_clickable((By.ID, "rbn_extent_0")))
            
            retry_count = 0
            while retry_count < 5:
                try:
                    rbn_extent_0.click()
                    logger.debug("✅ Radio button clicked")
                    break
                except:
                    logger.warning(f"⚠️ Radio button click failed (attempt {retry_count + 1})")
                    retry_count += 1
                    sleep(1)
            
            # Select extension reason
            logger.debug("📋 Selecting extension reason")
            ddl_extend_select = Select(self.wait.until(EC.presence_of_element_located((By.ID, "ddl_extend"))))
            ddl_extend_select.select_by_value('4')
            
            # Fill remarks
            logger.debug("📝 Filling remarks")
            txtRemarks = self.driver.find_element(By.ID, "txtRemarks")
            txtRemarks.clear()
            txtRemarks.send_keys("Transhipment")

            sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            # Get and fill location details
            logger.debug("📍 Processing location details")
            txtFromPincode = self.driver.find_element(By.ID, "txtFromPincode").get_attribute("value")
            slFromState = Select(self.driver.find_element(By.ID, "slFromState")).first_selected_option.text
            logger.debug(f"📍 From Pincode: {txtFromPincode}, State: {slFromState}")
            
            txt_vehFromPlace = self.driver.find_element(By.ID, "txt_vehFromPlace")
            txt_vehFromPlace.clear()
            txt_vehFromPlace.send_keys(slFromState)
            
            txtFromEnteredPinCode = self.driver.find_element(By.ID, "txtFromEnteredPinCode")
            txtFromEnteredPinCode.clear()
            txtFromEnteredPinCode.send_keys(txtFromPincode)
            
            # Get document details
            logger.debug("📄 Getting document details")
            ctl00_ContentPlaceHolder1_txtDocNo = self.wait.until(
                EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_txtDocNo"))
            ).get_attribute("value")
            
            txtDocDate = self.driver.find_element(By.ID, "txtDocDate").get_attribute("value")
            logger.debug(f"📄 Doc No: {ctl00_ContentPlaceHolder1_txtDocNo}, Doc Date: {txtDocDate}")

            # Fill vehicle details
            logger.debug(f"🚛 Filling vehicle details - Vehicle: {vehicle}")
            ctl00_ContentPlaceHolder1_txtVehicleNo = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtVehicleNo")
            ctl00_ContentPlaceHolder1_txtVehicleNo.clear()
            ctl00_ContentPlaceHolder1_txtVehicleNo.send_keys(vehicle)

            ctl00_ContentPlaceHolder1_txtTransDocNo = self.driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtTransDocNo")
            ctl00_ContentPlaceHolder1_txtTransDocNo.clear()
            ctl00_ContentPlaceHolder1_txtTransDocNo.send_keys(txtDocDate)

            # Fill distance
            logger.debug(f"📏 Filling distance: {kilo_meters} km")
            txtDistance = self.driver.find_element(By.ID, "txtDistance")
            sleep(2)
            txtDistance.clear()
            txtDistance.send_keys(str(kilo_meters))

            # Submit the form
            logger.debug("📤 Submitting extension form")
            btnsbmt = self.wait.until(EC.element_to_be_clickable((By.ID, "btnsbmt")))
            
            sleep(2)
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            
            retry_count = 0
            while retry_count < 5:
                try:
                    btnsbmt.click()
                    logger.debug("✅ Submit button clicked")
                    break
                except:
                    logger.warning(f"⚠️ Submit button click failed (attempt {retry_count + 1})")
                    retry_count += 1
                    sleep(1)

            # Wait for result and monitor status
            logger.debug("⏳ Waiting for extension result...")
            current_url = self.driver.current_url
            start_time = datetime.now()
            
            while True:
                try:
                    sleep(1)
                    self.handle_all_popups()
                    current_url = self.driver.current_url
                    
                    # Log URL changes
                    if current_url != "https://ewaybillgst.gov.in/BillGeneration/EwbExtension.aspx":
                        logger.debug(f"🌐 URL changed to: {current_url}")
                    
                    if current_url == "https://ewaybillgst.gov.in/BillGeneration/EwbExtension.aspx":
                        current_time = datetime.now()
                        elapsed_time = (current_time - start_time).total_seconds()
                        
                        # Log progress every 10 seconds
                        if int(elapsed_time) % 10 == 0:
                            logger.debug(f"⏳ Waiting... {int(elapsed_time)}s elapsed")
                        
                        if elapsed_time > 30:
                            logger.error(f"❌ Extension timeout for {eway_no} after {elapsed_time}s")
                            return False
                    else:
                        logger.info(f"✅ Extension successful for {eway_no}")
                        return True
                        
                except Exception as e:
                    logger.warning(f"⚠️ Error during status check: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"❌ Error extending eway {eway_no}: {str(e)}")
            logger.error(f"📋 Traceback: {traceback.format_exc()}")
            return False

# ============================================================================
# LOG INFORMATION GENERATOR
# ============================================================================

def generate_log_info():
    """Generate information about log files for customer support"""
    log_info = f"""
    
🔍 LOG FILES GENERATED:
========================
📂 Logs Directory: ./logs/
📋 Files created with timestamp: {datetime.now().strftime('%Y%m%d_%H%M%S')}

📝 LOG FILE TYPES:
==================
1. 🐛 debug_TIMESTAMP.log     - Complete detailed logs (Send this for debugging)
2. ❌ errors_TIMESTAMP.log    - Error logs only
3. 📋 operations_TIMESTAMP.log - Main operations summary
4. 📊 log.txt                 - Extension results summary

🚀 FOR TECHNICAL SUPPORT:
=========================
Please share the following files with support:
1. 🐛 debug_TIMESTAMP.log (Most important)
2. ❌ errors_TIMESTAMP.log
3. 📊 log.txt
4. 📋 Your user.json and eway.csv files (remove sensitive data)

📧 Contact: Shubham Malik
📋 Include: Error description, timestamp, and above log files
    """
    print(log_info)
    logger.info("📋 Log information generated for customer support")

# ============================================================================
# SCRIPT EXECUTION
# ============================================================================

if __name__ == "__main__":
    script_start_time = datetime.now()
    logger.info(f"🚀 Script execution started at: {script_start_time}")
    
    try:
        # Execute main automation
        automation_object = extendEwayBill()
        
        script_end_time = datetime.now()
        execution_time = script_end_time - script_start_time
        
        logger.info(f"✅ Script execution completed successfully")
        logger.info(f"⏱️ Total execution time: {execution_time}")
        
        # Generate log information for customer
        generate_log_info()
        
    except Exception as e:
        script_end_time = datetime.now()
        execution_time = script_end_time - script_start_time
        
        logger.error(f"🚫 Script execution failed: {str(e)}")
        logger.error(f"📋 Full traceback: {traceback.format_exc()}")
        logger.info(f"⏱️ Execution time before failure: {execution_time}")
        
        # Generate log information even on failure
        generate_log_info()
        
        print("\n" + "="*80)
        print("❌ SCRIPT FAILED - CHECK LOG FILES FOR DETAILS")
        print("📧 Send log files to support for assistance")
        print("="*80)
        
        sys.exit(1)
