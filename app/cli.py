import os
import click


def register(app):
    @app.cli.group()
    def translate():
        """Translation and localization commands."""
        pass

    def init(lang):
        """Initialize a new language."""
        print('register::init')

    @translate.command()
    def update():
        """Update all languages."""
        print('register::update')

    @translate.command()
    def compile():
        """Compile all languages."""
        print('register::compile')
