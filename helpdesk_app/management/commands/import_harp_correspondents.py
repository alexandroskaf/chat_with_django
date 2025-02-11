from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os

from helpdesk_app.models import *
import pandas as pd


########### DONE ##############

class Command(BaseCommand):
    def handle(self, *args, **options):
      help = 'Import all harp correspondents from the "HARPCORRESPONDENT_EXPORT.xlsx" file.'

      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return None

      print("Begin database population with new harp correspondents.")

      file = "HARPCORRESPONDENT_EXPORT.xlsx"
      # file = "test_harp_correspondent.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2, 3, 4, 5, 6]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        number = render_field(str(df.iat[i, 3]))
        if not number is None and not HarpCorrespondent.objects.filter(number=number).exists():
          correspondent = render_field(str(df.iat[i, 0]))
          if not correspondent is None:
            formation_input = render_field(str(df.iat[i, 1]))
            unit_input = render_field(str(df.iat[i, 2]))
            device_type = str(df.iat[i, 4])
            is_track_harp_input = df.iat[i, 5]
            if not is_track_harp_input is None:
              is_track_harp = is_track_harp_input
            else:
              is_track_harp = None
            
            formation_check = Unit.objects.filter(name=formation_input)
            if formation_check.exists():
              formation = formation_check.first()
            else:
              formation = None

            unit_check = Unit.objects.filter(name=unit_input)
            if unit_check.exists():
              unit = unit_check.first()
            else:
              unit = None

            new_harp_correspondent = HarpCorrespondent(
              correspondent = correspondent,
              formation = formation,
              unit = unit,
              number = number,
              device_type = device_type,
              is_track_harp = is_track_harp
            )
            new_harp_correspondent.save()
            print(f"The harp correspondent '{new_harp_correspondent}' was successfully created.")

          else:
            print("A harp correspondent had no name and therefore could not be created, aborting...")

        else:
          print(f"A harp correspondnt with the number {number} already exists, skipping...")

      print("The database was successfully updated, all new harp correspondents have now been created.")
