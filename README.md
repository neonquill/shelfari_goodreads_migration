# Shelfari to Goodreads migration fixup

Some hacked up code to fix the read dates and ratings for books that
were automatically transferred from Shelfari to Goodreads.

## Steps

Requires python 2.7 (or so).

```console
pip install -r requirements.txt
````

Export books from Shelfari into `My_Shelfari_Books.tsv`.

Create a `goodreads.cfg` file with the contents of your API keys and
OAuth tokens.

```ini
[goodreads]
api_key: <api_key>
api_secret: <api_secret>
access_token: <oauth_access_token>
access_token_secret: <oauth_access_token_secret>
```

Use the [goodreads](https://github.com/sefakilic/goodreads) api to
generate the access_token:

```python
import goodreads.client
gc = goodreads.client.GoodreadsClient(<api_key>, <api_secret>)
gc.authenticate()
print gc.session.access_token
print gc.session.access_token_secret
```

```console
./update.py
```
