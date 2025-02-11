from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os

from helpdesk_app.models import *
import pandas as pd

class Command(BaseCommand):
    help = 'Import all routings from the "ROUTING_EXPORT.xlsx" file.'

    def handle(self, *args, **options):

      print("Begin database population with new routings.")

      file = "ROUTING_EXPORT.xlsx"
      # file = "test_routing.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        name = str(df.iat[i, 0]).strip()
        print(f"Attempting to create new routing '{name}'...")
        if not Routing.objects.filter(name=name).exists():
          Routing(
            name = name,
          ).save()
          print(f"The routing '{name}' was successfully created.")
        else:
          print(f"The routing '{name}' already exists, skipping...")
      
      print("The database was successfully updated, all new routings have now been created.")
