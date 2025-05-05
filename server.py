"""
This is a GET and POST HTTP server
interacts with any internet browser through URLs

"""

import asyncio
import os
from urllib.parse import unquote


async def handleClient(reader, writer):
    data = await reader.read(1024)
    message = data.decode('utf-8')
    headers = message.split('\r\n')
    requestLine = headers[0]

    # Splits the request to obtain the method, URL path and other request scheme portions
    try:
        method, path, _ = requestLine.split()
    except ValueError:

        # 4** Status code
        response = (
            "HTTP/1.1 400 Bad Request\r\n"
            "Content-Type: text/html\r\n"
            "Content-Length: 62\r\n"
            "Connection: close\r\n"
            "\r\n"
            "<html><body><h1>400 Bad Request</h1><p>Malformed Syntax</p></body></html>"
        )
        writer.write(response.encode('uft-8'))
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return

    # Handles and calls the HTTP methods
    if method == 'GET':
        await getMethod(reader, writer, path)
    elif method == 'POST':
        await postMethod(reader, writer, path,  message)

async def getMethod(reader, writer, path):

 # Decodes URL-encoded path from it`s standard format
    path = unquote(path)
    path = path.split('?', 1)[0]
    resourcePath = os.path.normpath(path.lstrip('/'))

    # Sets index.html as the default page
    if resourcePath in ('', '.'):
        resourcePath = 'templates/index.html'

    # Identifies the directory whether user or home
    if resourcePath.startswith("~"):
        userDir, _, rest = resourcePath.partition('/')
        username = userDir[1:]
        baseDir = f"/home/{username}/templates"
        file_path = os.path.join(baseDir, rest)
    else:
        # Looks in the current working directory
        file_path = os.path.join(os.getcwd(), resourcePath)

    # Checks if the requested file exists and sends it
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            responseBody = f.read()

        if file_path.endswith(".html"):
            contentType = "text/html"
        else:
            contentType = "application/octet-stream"

        response = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {contentType}\r\n"
            f"Content-Length: {len(responseBody)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            ).encode('utf-8') + responseBody

        writer.write(response)
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        return

    # If file not found, returns 404 Not Found
    responseBody = "<html><body><h1>404 Not Found</h1><p>File not found</p></body></html>"
    response = (
        "HTTP/1.1 404 Not Found\r\n"
        "Content-Type: text/html\r\n"
        f"Content-Length: {len(responseBody.encode('utf-8'))}\r\n"
        "Connection: close\r\n"
        "\r\n"
        f"{responseBody}"
    )
    writer.write(response.encode('utf-8'))
    await writer.drain()
    writer.close()
    await writer.wait_closed()

# Handles the HTTP POST method
async def postMethod(reader, writer, path, message):

    if path == '/submit':
        try:

            headers = message.split('\r\n')
            requestLine = message.split("\r\n\r\n", 1)[1]

            # Extracts username & email address from read data
            username = requestLine.split('username=')[1].split('&')[0]
            email = requestLine.split('email=')[1].split('&')[0]

            # Saves to db.txt
            with open('db.txt', 'a') as dataBase:
                dataBase.write(f"{username},{email}\n")

            # 3** status code redirecting to index.html
            response = (
               "HTTP/1.1 302 Found\r\n"
                "Location: /templates/index.html?success=1\r\n"
                "Connection: close\r\n"
                "\r\n"
            )
            writer.write(response.encode('utf-8'))
            await writer.drain()

        # 5** status code, when there is an error
        except Exception as e:
            responseBody = "<html><body><h1>500 Internal Server Error</h1><p> The Server Encountered An Error</p><body></html"
            response = (
                "HTTP/1.1 500 Internal Server Error\r\n"
                "Content-Type: text/html\r\n"
                f"Content-Length: {len(responseBody.encode('utf-8'))}\r\n"
                "Connection: close\r\n"
                "\r\n"
                f"{responseBody}"
            )
            writer.write(response.encode('utf-8'))
            await writer.drain()

            print(f"error {e}") # debug flag

        finally:
            writer.close()
            await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handleClient, '127.0.0.1', 8080)
    print("HTTP Server running on http://127.0.0.1:8080")
    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
