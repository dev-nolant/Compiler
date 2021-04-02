import basic
while True:
    text=input('5u_lang > ')
    result, error = basic.run('<stdin>', text)

    if error: print(error.as_string())
    else: print(result)