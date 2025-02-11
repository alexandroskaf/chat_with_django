from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os

from helpdesk_app.models import *
import pandas as pd
import argparse

class Command(BaseCommand):
    help = 'Import all units from the "UNIT_EXPORT.xlsx" file.'
    # def add_arguments(self, parser):
    #     parser.add_argument('--file', type=argparse.FileType('r'))

    def handle(self, *args, **options):
      # file_path = options['file']

      print("Begin database population with new units.")

      file = "UNIT_EXPORT.xlsx"
      # file = "test_units.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2, 3, 4, 5, 6]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        name = str(df.iat[i, 0]).strip()
        print(f"Attempting to create new unit '{name}'...")
        if not Unit.objects.filter(name=name).exists():
          Unit(
            name = str(df.iat[i, 0]).strip(),
            location = str(df.iat[i, 1]).strip(),
            parent = None,
            major_formation = None,
            is_formation = df.iat[i, 4],
            is_major = df.iat[i, 5]
          ).save()
          print(f"Unit '{name}' was successfully created.")
        else:
          print(f"Unit '{name}' already exists, skipping...")

      for i in range(0, df_rows, 1):
        name = str(df.iat[i, 0]).strip()
        print(f"Updating the hierarchy for unit '{name}'...")
        parent_input = str(df.iat[i, 2]).strip()
        major_formation_input = str(df.iat[i, 3]).strip()

        if not Unit.objects.filter(name=parent_input).exists():
          print(f"The unit '{parent_input}' does not exist and therefore can't be used as a 'parent', aborting...")
        elif not Unit.objects.filter(name=major_formation_input).exists():
          print(f"The unit '{major_formation_input}' does not exist and therefore can't be used as a 'major_formation', aborting...")
        else:
          unit = Unit.objects.get(name=name)
          parent = Unit.objects.get(name=parent_input)
          major_formation = Unit.objects.get(name=major_formation_input)
          unit.parent = parent
          unit.major_formation = major_formation
          unit.save()
          print(f"The hierarchy for unit '{name}' was successfully updated.")

      print("The database was successfully updated, all new units have now been created.")
      print("Exiting...")
