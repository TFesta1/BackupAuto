from oauth2client.service_account import ServiceAccountCredentials
import gspread, random, time


documents_location = r"C:\Users\Tanner\Documents"
json_token_file_path = fr"{documents_location}\client_json_desktop.json"
basePath = fr"{documents_location}\BackupAuto\Data"
notebookName = "GithubLinks"
sheetName = "Desktop"

urlIndex = 0

def get_worksheet_backoff(gClient, googleSheetName, sheetName, max_attempts=5):
    for attempt in range(max_attempts):
        try:
            # print(dir(gClient.open(googleSheetName)))
            return gClient.open(googleSheetName).worksheet(sheetName)
        except Exception as e: #gspread.exceptions.APIError as e:
            if e.response.status_code == 429:
                sleep_time = 2 ** attempt + random.random()
                time.sleep(sleep_time)
            else:
                raise e

def getSheet(sheetName, notebookName):
    scope = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file'
        ]
    file_name = json_token_file_path
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    gClient = gspread.authorize(creds)
    
    googleSheetName = notebookName

    #Fetch the sheet
    # time.sleep(10000)
    sheet = get_worksheet_backoff(gClient, googleSheetName, sheetName)
    

    return sheet




def save_sheet_as_csv(sheet, local_path):
    # Get all values from the sheet
    all_values = sheet.get_all_values()
    
    # Create a CSV-formatted string
    csv_content = "\n".join([",".join(row) for row in all_values])
    
    # Save the content locally
    with open(local_path, 'w', encoding='utf-8') as file:
        file.write(csv_content)

    print(f"Sheet saved as CSV at: {local_path}")


def main():
    localSavePath = fr"{basePath}\{sheetName}.csv"
    dynamicGetSheet = getSheet(sheetName, notebookName)
    save_sheet_as_csv(dynamicGetSheet, localSavePath)
    return localSavePath
