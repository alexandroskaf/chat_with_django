from django.core.management.base import BaseCommand, CommandError
from argparse import RawTextHelpFormatter
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
import subprocess, os
from django.db.models import Q

from helpdesk_app.models import *
import pandas as pd


class Command(BaseCommand):
    def handle(self, *args, **options):
      help = 'Import all hermes connections from the "HERMESCONNECTION_EXPORT.xlsx" file.'

      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return None

      print("Begin database population with new hermes connections.")

      file = "HERMESCONNECTION_EXPORT.xlsx"
      # file = "test_hermes_connections.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2, 3]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        number = render_field(str(df.iat[i, 0]))
        if number is None:
          print("A hermes connection had no 'number' provided, aborting...")
        elif HermesConnection.objects.filter(number=number).exists():
          print(f"A duplicate hermes connection with the number {number} was found, skipping...")

        else:
          node_from_input = render_field(str(df.iat[i, 1]))
          node_to_input = render_field(str(df.iat[i, 2]))

          if node_from_input is None:
            node_from = None
          else:
            node_from_check = HermesNode.objects.filter(number=node_from_input.split(" ")[0])
            if node_from_check.exists():
              node_from = node_from_check.first()
            else:
              node_from = None

          if node_to_input is None:
            node_to = None
          else:
            node_to_check = HermesNode.objects.filter(number=node_to_input.split(" ")[0])
            if node_to_check.exists():
              node_to = node_to_check.first()
            else:
              node_to = None


          new_hermes_connection = HermesConnection(
            number = number,
            node_from = node_from,
            node_to = node_to,
          )
          new_hermes_connection.save()
          print(f"The hermes connection '{new_hermes_connection}' was successfully created.")

      print("The database was successfully updated, all new hermes connections have now been created.")
