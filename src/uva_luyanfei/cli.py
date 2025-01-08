import click

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    return

@main.command()
@click.pass_context
def help(ctx):
    click.echo(ctx.parent.get_help())

if __name__ == '__main__':
    main()
