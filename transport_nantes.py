from app import create_app, cli

app = create_app()
cli.register(app)


@app.shell_context_processor
def make_shell_context():
    return {'Notification': Notification}
