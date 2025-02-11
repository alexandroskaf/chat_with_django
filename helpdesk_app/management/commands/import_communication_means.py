from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os

from helpdesk_app.models import *
import pandas as pd

class Command(BaseCommand):
    help = 'Import all communication means from the "COMMUNICATIONMEANS_EXPORT.xlsx" file.'

    def handle(self, *args, **options):

      print("Begin database population with new communication means.")

      file = "COMMUNICATIONMEANS_EXPORT.xlsx"
      # file = "test_communicationmeans.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        name = str(df.iat[i, 0]).strip()
        print(f"Attempting to create new communication means '{name}'...")
        if not CommunicationMeans.objects.filter(name=name).exists():
          CommunicationMeans(
            name = name,
          ).save()
          print(f"The communication means '{name}' was successfully created.")
        else:
          print(f"The communication means '{name}' already exists, skipping...")
      
      print("The database was successfully updated, all new communication means have now been created.")
