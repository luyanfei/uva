import click
import os
from bs4 import BeautifulSoup
import subprocess
import urllib.parse
from pathlib import Path

cookie_file = os.path.expanduser('~/.ojcookie')

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help']
)

def load_data():
    """
    format of the file: pnum~pid~title
    return a dict with pid as key and pnum, title as tuple value
    """
    path = Path(__file__).parent / 'data/pid-to-num.cvs'
    data = {}
    with open(path, 'r') as f:
        for line in f:
            pnum, pid, title = line.strip().split('~')
            data[pid] = (pnum, title)
    return data

@click.group(context_settings=CONTEXT_SETTINGS)
def main():
    return

@main.command()
@click.pass_context
def help(ctx):
    click.echo(ctx.parent.get_help())

@main.command()
def login():
    """
    Login with the given username and password
    """
    username = click.prompt('Username: ', type=str)
    password = click.prompt('Password: ', type=str, hide_input=True)
    loginurl = "https://onlinejudge.org/index.php?option=com_comprofiler&task=login";
    response1 = subprocess.run(
        ['curl', '-s', loginurl],
        capture_output=True,
        text=True
    )
    # find all hidden input fields
    soup = BeautifulSoup(response1.stdout, 'html.parser')
    loginform = soup.find('form', id='mod_loginform')
    hiddens = {i['name']: i['value'] for i in loginform.find_all('input', type='hidden')}

    form_data = {
        'username': username,
        'passwd': password,
        'remember': 'yes',
        'Submit': 'Login',
    }
    form_data.update(hiddens)
    encoded_data = urllib.parse.urlencode(form_data).encode('utf-8')
    # use curl to login, because requests doesn't work
    result = subprocess.run(
        ['curl', '-s', '-v', '-c', cookie_file, '-d', encoded_data, '-X', 'POST', loginurl],
        capture_output=True,
        text=True
    )
    # if result.stdout contains "HTTP/1.1 301 Moved Permanently" and "Location: https://onlinejudge.org/", then login is success
    if 'HTTP/1.1 301 Moved Permanently' in result.stdout and 'Location: https://onlinejudge.org/' in result.stdout:
        click.echo('Login success')
    else:
        click.echo('Login failed')

    
@main.command()
def logout():
    """
    Logout the current user
    """
    # remove the cookie file
    os.remove(cookie_file)

@main.command()
@click.option('--pid', '-p', type=str, help='Problem ID')
@click.option('--file', '-f', type=str, help='Source file')
@click.option('--lang', '-l', type=str, help='Language of the source file', default='C++11')
def submit(pid, file, lang='C++11'):
    """
    Submit the solution
    """
    if not os.path.exists(cookie_file):
        click.echo('Please login first')
        return
    lang_map = {
        'C': '1',
        'Java': '2',
        'C++': '3',
        'PASCAL': '4',
        'C++11': '5',
        'Python3': '6',
    }
    lang = lang_map.get(lang, '5')
    submiturl = "https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=25&page=save_submission"
    result = subprocess.run(
        [
            'curl', '-s', '-v',
            '-b', cookie_file, 
            '--form', f'localid={pid}', 
            '--form', f'language={lang}', 
            '--form', f'codeupl=@{file}',
            submiturl
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    # find the location header in the response
    location = None
    for line in result.stdout.split('\n'):
        if line.startswith('< Location:'):
            location = line
            break
    if not location:
        click.echo('No location header found')
        return
    # get the mosmsg parameter in the location header
    mosmsg = urllib.parse.parse_qs(urllib.parse.urlparse(location).query).get('mosmsg', [''])[0]
    click.echo(mosmsg)

@main.command()
@click.option('--pid', '-p', type=str, help='Problem ID')
def download(pid):
    """
    Download the pdf file of the problem with the given problem ID
    """
    if not pid:
        click.echo('Problem ID is required')
        return
    data = load_data()
    pnum, _ = data.get(pid, (None, None))
    if not pnum:
        click.echo('Problem ID is not in the list.')
        return
    url = f'https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=8&page=show_problem&problem={pnum}'
    result = subprocess.run(
        ['curl', '-s', '-b', cookie_file, url],
        capture_output=True,
        text=True
    )
    soup = BeautifulSoup(result.stdout, 'html.parser')
    # find the first iframe in the element with id "col3"
    iframe = soup.find('div', id='col3').find('iframe')
    if not iframe:
        click.echo('No iframe found')
        return
    # pdfurl is the src attribute of the iframe with "pdf" as the postfix instead of "html"
    pdfurl = 'https://onlinejudge.org/' + iframe['src'].replace('html', 'pdf')
    click.echo(f'Downloading {pdfurl}')
    # download the pdf file use curl
    result = subprocess.run(
        ['curl', '-s', '-b', cookie_file, pdfurl, '-o', f'{pid}.pdf'],
        capture_output=True,
        text=True
    )
    click.echo(f'{pid}.pdf downloaded')

@main.command()
def status():
    """
    Show the status of the last 30 submissions
    """
    if not os.path.exists(cookie_file):
        click.echo('Please login first')
        return
    statusurl = "https://onlinejudge.org/index.php?option=com_onlinejudge&Itemid=9"
    result = subprocess.run(
        ['curl', '-s', '-b', cookie_file, statusurl],
        capture_output=True,
        text=True
    )
    soup = BeautifulSoup(result.stdout, 'html.parser')
    # find first table in the element with id "col3_content_wrapper"
    table = soup.find('div', id='col3_content_wrapper').find('table')
    if not table:
        click.echo('No status table found')
        return
    # find all rows in the table
    rows = table.find_all('tr')
    # find all columns max width
    col_widths = []
    for row in rows:
        cols = row.find_all('td')
        if not cols:
            continue
        # initialize col_widths with length of the first row
        if not col_widths:
            col_widths = [len(col.text.strip()) for col in cols]
        for i, col in enumerate(cols):
            if len(col.text.strip()) > col_widths[i]:
                col_widths[i] = len(col.text.strip())
    # print all columns with the max width plus 2 spaces
    for row in rows:
        cols = row.find_all('td')
        if not cols:
            continue
        for i, col in enumerate(cols):
            click.echo(col.text.strip().ljust(col_widths[i] + 2), nl=False)
            click.echo('\t', nl=False)
        click.echo()


if __name__ == '__main__':
    main()
