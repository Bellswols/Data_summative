
# Importing necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
from shiny import App, render, ui

# Data processing

df = pd.read_csv('my_file.csv')

# Make sure Date is a datetime type
df['Date'] = pd.to_datetime(df['Date'])

# Clean the 'Has Attended' column and create a numeric attendance column
df['Has Attended'] = (
    df['Has Attended']
    .astype(str)
    .str.strip()
    .str.upper()
)

df = df[df['Has Attended'].isin(['Y', 'N'])]
df['Attendance'] = df['Has Attended'].map({'Y': 1, 'N': 0})

module_choices = sorted(df['Module Name'].unique())

# Ui


app_ui = ui.page_fluid(
    ui.h2('Attendance Rate Over Time'),

    ui.input_selectize(
        'module_select',
        'Select module(s):',
        choices=module_choices,
        multiple=True
    ),

    ui.output_plot('attendance_plot')
)


# Server

def server(input, output, session):

    @output
    @render.plot
    def attendance_plot():
        selected_modules = input.module_select()

        # If nothing is selected, show a placeholder plot
        if not selected_modules:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.set_title('Please select at least one module.')
            ax.set_xlabel('Date')
            ax.set_ylabel('Average Attendance Rate')
            return fig

        # ✅ Create ONE figure and axes
        fig, ax = plt.subplots(figsize=(8, 4))

        # ✅ Loop through modules and plot them on the SAME axes
        for module in selected_modules:
            df_module = df[df['Module Name'] == module]

            attendance_rate = (
                df_module
                .groupby('Date', as_index=False)['Attendance']
                .mean()
                .sort_values('Date')
            )

            ax.plot(
                attendance_rate['Date'],
                attendance_rate['Attendance'],
                marker='o',
                label=module,
            )

        # Shared formatting
        ax.set_title('Attendance Rate Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Average Attendance Rate')
        ax.grid(True)
        ax.tick_params(axis='x', rotation=45)
        ax.legend(title='Module')

        return fig

app = App(app_ui, server)
