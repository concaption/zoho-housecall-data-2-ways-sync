"""
path: main/sheet.py
author: @concaption
date: 2023-10-18
description: This module contains functions for creating, reading, updating, and
sharing Google Sheets.
"""

import time
import logging
from oauth2client.service_account import ServiceAccountCredentials as SAC
import gspread
import pandas as pd
import gspread_dataframe as gd


logger = logging.getLogger(__name__)


class SheetsClient:
    """
    Class for connecting to a Google Sheet and performing operations on it.
    """
    def __init__(self, credentials_file_path, scope=None):
        self.credentials_file_path = credentials_file_path
        self.scope = scope or [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
            ]
        self.credentials = SAC.from_json_keyfile_name(self.credentials_file_path, self.scope)
        self.gc = gspread.authorize(self.credentials)

    def get_or_create_sheet(self, sheet_name, spreadsheet_name, obj=False, size='0'):
        """
        Get or create sheet
        """
        try:
            spreadsheet = self.gc.open(spreadsheet_name)
        except gspread.exceptions.SpreadsheetNotFound:
            spreadsheet = self.gc.create(spreadsheet_name)
            # Share sheet with service account email
            self.share_sheet(spreadsheet.id, "concaption@gmail.com")
        try:
            sheet = spreadsheet.worksheet(sheet_name)
        except gspread.exceptions.WorksheetNotFound:
            sheet = spreadsheet.add_worksheet(title=sheet_name, rows=size, cols=size)
        sheet_id = sheet.id
        spreadsheet_id = spreadsheet.id
        if obj:
            return sheet, spreadsheet
        return sheet_id, spreadsheet_id

    def get_sheet(self, sheet_id, spreadsheet_id):
        """
        Get sheet
        """
        spreadsheet = self.gc.open_by_key(spreadsheet_id)
        sheet = spreadsheet.get_worksheet_by_id(sheet_id)
        return sheet

    def get_sheet_values(self, sheet_id, spreadsheet_id, dataframe=True):
        """
        Get Sheet Values as a DataFrame or a list
        """
        sheet = self.get_sheet(sheet_id, spreadsheet_id)
        values = sheet.get_all_values()
        data_frame = pd.DataFrame(values[1:], columns=values[0])
        if dataframe:
            return data_frame
        return values

    def append_row(self, sheet_name, spreadsheet_name, row, timestamp=True):
        """
        Append row only if the row doesn't exist
        """
        sheet, _ = self.get_or_create_sheet(sheet_name, spreadsheet_name, obj=True)
        if timestamp:
            row.insert(0,time.strftime("%Y-%m-%d %H:%M:%S"))
        sheet.append_row(row)
        return True

    def add_deal(self, sheet_name, spreadsheet_name, deal_dict):
        sheet, _ = self.get_or_create_sheet(sheet_name, spreadsheet_name, obj=True)
        existing_values = gd.get_as_dataframe(sheet)
        existing_values.dropna(how='all', inplace=True)
        existing_values.dropna(axis=1, how='all', inplace=True)
        deal_id = deal_dict.get("deal_id")
        if deal_id in existing_values["deal_id"].tolist():
            logger.info("Appointment for deal_id %s already exists. Replacing...", deal_id)
            existing_values = existing_values[existing_values["deal_id"] != deal_id]
        new_row = pd.DataFrame([deal_dict])
        updated_values = pd.concat([existing_values, new_row], ignore_index=True)
        print(existing_values)
        gd.set_with_dataframe(sheet, updated_values)
        return True

    def share_sheet(self, spreadsheet_id, email):
        """
        Share sheet with email
        """
        sh = self.gc.open_by_key(key=spreadsheet_id)
        sh.share(email, perm_type='user', role='writer')
        return True
