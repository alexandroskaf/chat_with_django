from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os

from helpdesk_app.models import *
import pandas as pd

class Command(BaseCommand):
    help = 'Import all broadband transceivers from the "BROADBANDTRANSCEIVER_EXPORT.xlsx" file.'

    def handle(self, *args, **options):
      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return None

      print("Begin database population with new broadband transceivers.")

      file = "BROADBANDTRANSCEIVER_EXPORT.xlsx"
      # file = "test_broadband_transceiver.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2, 3, 4, 5, 6, 7]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        hostname = render_field(str(df.iat[i, 0]).strip())
        if not hostname is None:
          print(f"Attempting to create new broadband transceiver '{hostname}'...")
          if not BroadbandTransceiver.objects.filter(hostname=hostname).exists():
            coupling = render_field(str(df.iat[i, 1]).strip())
            coupling_code = render_field(str(df.iat[i, 2]).strip())
            model = render_field(str(df.iat[i, 3]).strip())
            formation_input = render_field(str(df.iat[i, 4]).strip())
            unit_from_input = render_field(str(df.iat[i, 5]).strip())
            unit_to_input = render_field(str(df.iat[i, 6]).strip())

            formation_check = Unit.objects.filter(name=formation_input)
            if formation_check.exists():
              formation = formation_check.first()
            else:
              formation = None

            unit_from_check = Unit.objects.filter(name=unit_from_input)
            if unit_from_check.exists():
              unit_from = unit_from_check.first()
            else:
              unit_from = None

            unit_to_check = Unit.objects.filter(name=unit_to_input)
            if unit_to_check.exists():
              unit_to = unit_to_check.first()
            else:
              unit_to = None

            new_broadband_transceiver = BroadbandTransceiver(
              hostname = hostname,
              coupling = coupling,
              coupling_code = coupling_code,
              model = model,
              formation = formation,
              unit_from = unit_from,
              unit_to = unit_to,
            )
            new_broadband_transceiver.save()
            print(f"The broadband transceiver '{new_broadband_transceiver}' was successfully created.")

          else:
            print(f"The broadband transceiver '{hostname}' already exists, skipping...")
      
      print("The database was successfully updated, all new broadband transceivers  have now been created.")
