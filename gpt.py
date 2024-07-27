
import g4f

def ask_gpt(prom: str) -> str:
    response = g4f.ChatCompletion.create(
        model=g4f.models.default,
        messages=[{"role": "user", "content": prom}],
        # proxy="http://host:port",
        # proxy="socks5://user:pass@host:port",
        timeout=120, # in secs
    )
    return response
    print(f"Result:", response)

if __name__ == '__main__':

    # prom = "Переведи initializer for ctype 'void *' must be a cdata pointer, not NoneType"
    prom = 'Привет'
    ask_gpt(prom)
