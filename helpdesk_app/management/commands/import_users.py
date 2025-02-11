from django.contrib.auth.management.commands import createsuperuser
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
import subprocess, os

from helpdesk_app.models import *

import pandas as pd

# EXAMPLE USAGE
# python3 manage.py create_users --username test1 --password 123321 --noinput --email 'blank@email.com'

class Command(BaseCommand):
    help = 'Import all users and their details from an .xlsx file.'

    def handle(self, *args, **options):
      def get_or_create_user_group(name):
        user_group, created = Group.objects.get_or_create(name = name)
        if created:
          print(f"Created new '{name}' user group.")
        else:
          print(f"A user group called '{name}' was already created.")
        return user_group    
     
      def render_field(maybe_not_empty):
        if not maybe_not_empty == "":
          return maybe_not_empty
        return ""

      def add_user_to_user_groups(user, is_admin, is_manager, is_dispatcher, is_ddb, is_simple_user):
        if is_admin:
          user.groups.add(admin_group)
        if is_manager:
          user.groups.add(manager_group)
        if is_dispatcher:
          user.groups.add(dispatcher_group)
        if is_ddb:
          user.groups.add(ddb_group)
        if is_simple_user:
          user.groups.add(simple_user_group)        
 
      print("Initializing...")
      print("Begin database population with new users.")

      User = get_user_model()
      # file = "test_users.xlsx"
      file = "CUSTOMUSER_EXPORT.xlsx"
      # file_path = "/usr/app_files/" + file
      file_path = f"{os.environ.get('APP_HOME')}/../app_files/" + file

      df = pd.read_excel(
        file_path, 
        usecols=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 
        converters={"phone":str}
      ).fillna("")
      
      df_rows = df.shape[0]

      admin_group = get_or_create_user_group("admins")
      manager_group = get_or_create_user_group("managers")
      dispatcher_group = get_or_create_user_group("dispatchers")
      ddb_group = get_or_create_user_group("ddb")
      simple_user_group = get_or_create_user_group("users")

      for i in range(0, df_rows, 1):
        is_admin = df.iat[i, 8]
        is_manager = df.iat[i, 9]
        is_dispatcher = df.iat[i, 10]
        is_ddb = df.iat[i, 11]
        is_simple_user = df.iat[i, 12]

        username = str(df.iat[i, 0]).strip()
        password = str(df.iat[i, 1]).strip()
        email = render_field(str(df.iat[i, 6]).strip())

        if not User.objects.filter(username=username).exists():
          if is_admin:
            user = User.objects.create_superuser(username=username, email=email, password=password)
          else:
            user = User.objects.create_user(username=username, email=email, password=password)

          user.first_name = render_field(str(df.iat[i, 2]).strip())
          user.last_name = render_field(str(df.iat[i, 3]).strip())
          user.unit = Unit.objects.filter(name=str(df.iat[i, 4]).strip()).first()
          user.phone = render_field(str(df.iat[i, 5]).strip())
          means_list_input = render_field(str(df.iat[i, 7]).strip())
          if not means_list_input is None:
            means_list = means_list_input.split(",")
          else:
            means_list = None
          
          if not means_list is None and means_list:
            for means in means_list:
              means_to_add_input = CommunicationMeans.objects.filter(name=means)
              if means_to_add_input.exists():
                user.means.add(means_to_add_input.first())

          add_user_to_user_groups(user, is_admin, is_manager, is_dispatcher, is_ddb, is_simple_user)
          user.save()
          print(f"User {username} was created successfully.")
        else:
          print(f"User {username} already exists, skipping...")
      
      print("The database was successfully updated, all new users have now been created.")
      print("Exiting...")