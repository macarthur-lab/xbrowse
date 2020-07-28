# -*- coding: utf-8 -*-
# Generated by Django 1.11.28 on 2020-02-11 16:26
from tqdm import tqdm
from guardian.shortcuts import remove_perm, assign_perm, get_groups_with_perms
from django.db import migrations, models
from django.contrib.auth.models import User

from seqr.models import CAN_VIEW, CAN_EDIT, IS_OWNER, Project as ExistingProject


def add_projects_to_locus_lists(apps, schema_editor):
    LocusList = apps.get_model("seqr", "LocusList")
    Project = apps.get_model("seqr", "Project")
    db_alias = schema_editor.connection.alias
    locus_lists = LocusList.objects.using(db_alias).all()
    if locus_lists:
        print('Updating permissions for {} locus lists'.format(len(locus_lists)))
        for locus_list in tqdm(locus_lists, unit=' locus lists'):
            groups = get_groups_with_perms(locus_list)
            existing_project_guids = {p.guid for p in ExistingProject.objects.filter(can_view_group__in=groups).only('guid')}
            locus_list.projects = Project.objects.filter(guid__in=existing_project_guids)
            locus_list.save()
            if locus_list.created_by_id:
                user = User.objects.get(id=locus_list.created_by_id)
                remove_perm(user_or_group=user, perm=IS_OWNER, obj=locus_list)
                remove_perm(user_or_group=user, perm=CAN_EDIT, obj=locus_list)
                remove_perm(user_or_group=user, perm=CAN_VIEW, obj=locus_list)


def add_permissions_to_locus_lists(apps, schema_editor):
    LocusList = apps.get_model("seqr", "LocusList")
    db_alias = schema_editor.connection.alias
    locus_lists = LocusList.objects.using(db_alias).all()
    if locus_lists:
        print('Updating permissions for {} locus lists'.format(len(locus_lists)))
        for locus_list in tqdm(locus_lists, unit=' locus lists'):
            for project in locus_list.projects:
                assign_perm(user_or_group=project.can_view_group, perm=CAN_VIEW, obj=locus_list)
            if locus_list.created_by:
                user = User.objects.get(id=locus_list.created_by_id)
                assign_perm(user_or_group=user, perm=IS_OWNER, obj=locus_list)
                assign_perm(user_or_group=user, perm=CAN_EDIT, obj=locus_list)
                assign_perm(user_or_group=user, perm=CAN_VIEW, obj=locus_list)


class Migration(migrations.Migration):

    dependencies = [
        ('seqr', '0004_auto_20200124_1912'),
    ]

    operations = [
        migrations.AddField(
            model_name='locuslist',
            name='projects',
            field=models.ManyToManyField(to='seqr.Project'),
        ),
        migrations.RunPython(add_projects_to_locus_lists, reverse_code=add_permissions_to_locus_lists),
    ]
