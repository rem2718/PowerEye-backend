# PowerEye Backend

Common HTTP status codes: 
200 OK
The request was successful. This is the standard response for a successful HTTP request.

201 Created
The request has been fulfilled, resulting in the creation of a new resource.

204 No Content
The server successfully processed the request but there is no content to send in the response.

400 Bad Request
The server cannot understand or process the request due to a client error (e.g., malformed request syntax, invalid request message framing).

401 Unauthorized
The client must authenticate itself to get the requested response. This is often used for APIs that require authentication.

403 Forbidden
The client does not have the necessary permissions to access the requested resource.

404 Not Found
The server cannot find the requested resource. It is one of the most common error messages on the internet.

405 Method Not Allowed
The request method (e.g., GET, POST, PUT) is not supported for the requested resource.

429 Too Many Requests
The user has sent too many requests in a given amount of time ("rate limiting").

500 Internal Server Error
A generic error message indicating that something has gone wrong on the server, but the server cannot be more specific about the error.

502 Bad Gateway
The server, while acting as a gateway or proxy, received an invalid response from an upstream server it accessed in attempting to fulfill the request.

503 Service Unavailable
The server is not ready to handle the request. Common causes include the server being down for maintenance or being overloaded.

504 Gateway Timeout
The server, while acting as a gateway or proxy, did not receive a timely response from the upstream server or some other auxiliary server it needed to access in order to complete the request.