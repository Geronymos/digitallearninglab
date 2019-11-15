# Generated by Django 2.2.7 on 2019-11-15 14:33

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='additional_info',
            field=models.TextField(blank=True, null=True, verbose_name='Hinweise/Anmerkungen/Hintergrund'),
        ),
        migrations.AlterField(
            model_name='content',
            name='learning_goals',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=850), blank=True, default=list, null=True, size=None, verbose_name='Lernziele'),
        ),
        migrations.AlterField(
            model_name='teachingmodule',
            name='differentiating_attribute',
            field=models.TextField(blank=True, null=True, verbose_name='Differenzierung'),
        ),
        migrations.AlterField(
            model_name='teachingmodule',
            name='equipment',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=350), blank=True, default=list, null=True, size=None, verbose_name='Ausstattung'),
        ),
        migrations.AlterField(
            model_name='teachingmodule',
            name='estimated_time',
            field=models.CharField(blank=True, max_length=300, null=True, verbose_name='Zeitumfang'),
        ),
        migrations.AlterField(
            model_name='teachingmodule',
            name='expertise',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=1500), blank=True, default=list, null=True, size=None, verbose_name='Fachkompetenzen'),
        ),
        migrations.AlterField(
            model_name='teachingmodule',
            name='state',
            field=models.CharField(blank=True, choices=[('baden-wuerttemberg', 'Baden-Württemberg'), ('bayern', 'Bayern'), ('berlin', 'Berlin'), ('brandenburg', 'Brandenburg'), ('bremen', 'Bremen'), ('hamburg', 'Hamburg'), ('hessen', 'Hessen'), ('mecklenburg-vorpommern', 'Mecklenburg-Vorpommern'), ('niedersachsen', 'Niedersachsen'), ('nordrhein-westfalen', 'Nordrhein-Westfalen'), ('rheinland-pfalz', 'Rheinland-Pfalz'), ('saarland', 'Saarland'), ('sachsen', 'Sachsen'), ('sachsen-anhalt', 'Sachsen-Anhalt'), ('schleswig-holstein', 'Schleswig-Holstein'), ('thueringen', 'Thüringen')], max_length=22, null=True, verbose_name='Bundesland'),
        ),
        migrations.AlterField(
            model_name='teachingmodule',
            name='subject_of_tuition',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=2000), blank=True, default=list, null=True, size=None, verbose_name='Unterichtsgegenstand'),
        ),
        migrations.AlterField(
            model_name='tool',
            name='contra',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=300), blank=True, default=list, null=True, size=None, verbose_name='Kontra'),
        ),
        migrations.AlterField(
            model_name='tool',
            name='pro',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=300), blank=True, default=list, null=True, size=None, verbose_name='Pro'),
        ),
        migrations.AlterField(
            model_name='trend',
            name='publisher',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=300), blank=True, default=list, null=True, size=None, verbose_name='Herausgeber'),
        ),
        migrations.AlterField(
            model_name='trend',
            name='target_group',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=300), blank=True, default=list, null=True, size=None, verbose_name='Zielgruppe'),
        ),
    ]
