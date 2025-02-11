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
      help = 'Import all pyrseia servers from the "PYRSEIASERVER_EXPORT.xlsx" file.'

      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return None

      print("Begin database population with new pyrseia servers.")

      file = "PYRSEIASERVER_EXPORT.xlsx"
      # file = "test_pyrseia_servers.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(file_path, usecols=[1, 2, 3, 4, 5, 6, 7]).fillna("")
      df_rows = df.shape[0]

      for i in range(0, df_rows, 1):
        domain = render_field(str(df.iat[i, 3]))
        exchange = render_field(str(df.iat[i, 4]))
        esxi = render_field(str(df.iat[i, 5]))
        default_gateway = render_field(str(df.iat[i, 6]))
        if domain is None:
          print("A pyrseia server had no 'domain' provided, aborting...")
        elif exchange is None:
          print("A pyrseia server had no 'exchange' provided, aborting...")
        elif esxi is None:
          print("A pyrseia server had no 'esxi' provided, aborting...")
        elif default_gateway is None:
          print("A pyrseia server had no 'default_gateway' provided, aborting...")

        elif PyrseiaServer.objects.filter(
            Q(domain=domain) | 
            Q(exchange=exchange) | 
            Q(esxi=esxi) | 
            Q(default_gateway=default_gateway)
          ).exists():
          print(f"A duplicate pyrseia server was found, either 'domain', 'exchange', 'esxi' or 'default_gateway' was the same, skipping...")
        
        else:
          name = render_field(str(df.iat[i, 0]))
          formation_input = render_field(str(df.iat[i, 1]))
          unit_input = render_field(str(df.iat[i, 2]))

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

          new_pyrseia_server = PyrseiaServer(
            name = name,
            formation = formation,
            unit = unit,
            domain = domain,
            exchange = exchange,
            esxi = esxi,
            default_gateway = default_gateway
          )
          new_pyrseia_server.save()
          print(f"The pyrseia server '{new_pyrseia_server}' was successfully created.")

      print("The database was successfully updated, all new pyrseia servers have now been created.")
