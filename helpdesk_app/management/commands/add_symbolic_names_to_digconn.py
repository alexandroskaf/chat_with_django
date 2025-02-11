from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os

from helpdesk_app.models import *
import pandas as pd


######### DONE ##############


class Command(BaseCommand):
    def handle(self, *args, **options):
        print("parse initiated")

        # TEMPLATE FOR WRITING TO EXCEL
        # querySet = DigConnection.objects.all()
        # data = [{"number": dig.number, "formation": str(dig.formation), "unit_from": str(dig.unit_from), "unit_to": str(dig.unit_to)} for dig in querySet]
        # df = pd.DataFrame(data)
        # df.to_excel(file_path)

        file = "ΣΥΜΒΟΛΙΚΑ ΟΝΟΜΑΤΑ ΣΥΝΔΕΣΕΩΝ DIGCONNECTION.xlsx"
        file_path = "~/Documents/" + file

        df = pd.read_excel(file_path, usecols=[1, 3, 4]).fillna("---")
        df_rows = df.shape[0]

        for i in range(1, df_rows, 1):
            number_input = df.iat[i, 0]
            unit_from_input = str(df.iat[i, 1]).strip()
            unit_to_input = str(df.iat[i, 2]).strip()

            symbolic_name = f"{unit_from_input} - {unit_to_input}"
            dig_connection = DigConnection.objects.get(number=str(number_input))
            dig_connection.name = symbolic_name
            dig_connection.save()

