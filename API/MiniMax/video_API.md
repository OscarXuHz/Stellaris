> ## Documentation Index
> Fetch the complete documentation index at: https://platform.minimax.io/docs/llms.txt
> Use this file to discover all available pages before exploring further.

# Create Text-to-Video Generation Task

> Use this API to create a video generation task from text input.



## OpenAPI

````yaml api-reference/video/generation/api/text-to-video.json post /v1/video_generation
openapi: 3.1.0
info:
  title: MiniMax API
  description: MiniMax video generation and file management API
  license:
    name: MIT
  version: 1.0.0
servers:
  - url: https://api.minimax.io
security:
  - bearerAuth: []
paths:
  /v1/video_generation:
    post:
      tags:
        - Video
      summary: Video Generation
      operationId: videoGeneration
      parameters:
        - name: Content-Type
          in: header
          required: true
          description: >-
            The media type of the request body. Must be set to
            `application/json` to ensure the data is sent in JSON format.
          schema:
            type: string
            enum:
              - application/json
            default: application/json
      requestBody:
        description: ''
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/VideoGenerationReq'
        required: true
      responses:
        '200':
          description: ''
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/VideoGenerationResp'
components:
  schemas:
    VideoGenerationReq:
      type: object
      required:
        - model
        - prompt
      properties:
        model:
          type: string
          description: >-
            Model name. Supported values:

            `MiniMax-Hailuo-2.3`, `MiniMax-Hailuo-02`, `T2V-01-Director`,
            `T2V-01`.
          enum:
            - MiniMax-Hailuo-2.3
            - MiniMax-Hailuo-02
            - T2V-01-Director
            - T2V-01
        prompt:
          type: string
          description: "Text description of the video, up to 2000 characters.  \r\nFor `MiniMax-Hailuo-2.3`, `MiniMax-Hailuo-02` and `T2V-01-Director` models, camera movement can be controlled using `[command]` syntax.\n- **Supported 15 camera commands**:\n\t- Truck: `[Truck left]`, `[Truck right]`\n\t- Pan: `[Pan left]`, `[Pan right]`\n\t- Push: `[Push in]`, `[Pull out]`\n\t- Pedestal: `[Pedestal up]`, `[Pedestal down]`\n\t- Tilt: `[Tilt up]`, `[Tilt down]`\n\t- Zoom: `[Zoom in]`, `[Zoom out]`\n\t- Shake: `[Shake]`\n\t- Follow: `[Tracking shot]`\n\t- Static: `[Static shot]`\n\r\n- **Usage rules**: \n  - *Combined movements*: Multiple commands inside one `[]` take effect simultaneously (e.g., `[Pan left,Pedestal up]`). Recommended max: 3. \n  - *Sequential movements*: Commands appear in order, e.g., `\"...[Push in], then...[Push out]\"`. \n  - *Natural language*: Free-form descriptions also work, but explicit commands yield more accurate results.  "
        prompt_optimizer:
          type: boolean
          description: >-
            Whether to automatically optimize the `prompt`. Defaults to `true`.
            Set to `false` for more precise control.
        fast_pretreatment:
          type: boolean
          description: >-
            Reduces optimization time when `prompt_optimizer` is enabled.
            Defaults to `false`. Applies only to `MiniMax-Hailuo-2.3` and
            `MiniMax-Hailuo-02`.
        duration:
          type: integer
          description: >-
            Video length (seconds). Default is `6`. Available values depend on
            model and resolution:

            | Model |  720P |768P | 1080P |

            | :--- |:--- |:--- | :--- |

            | MiniMax-Hailuo-2.3 | - | `6` or `10` | `6` |

            | MiniMax-Hailuo-02 | - | `6` or `10` | `6` |

            | Other models | `6` | - |`6` |  
        resolution:
          type: string
          description: >-
            Video resolution. Options depend on model and duration:

            | Model | 6s | 10s |

            | :--- | :--- | :--- |

            | MiniMax-Hailuo-2.3 |  `768P` (default), `1080P` |  `768P`
            (default) |

            | MiniMax-Hailuo-02 |  `768P` (default), `1080P` |  `768P` (default)
            |

            | Other models | `720P` (default) | Not supported |
          enum:
            - 720P
            - 768P
            - 1080P
        callback_url:
          type: string
          description: "A callback URL to receive asynchronous task status updates.\n1. **Validation**: Once configured, MiniMax sends a `POST` request with a `challenge` field. Your server must echo this value within 3s to validate.\n2. **Updates**: After validation, MiniMax pushes status updates when the task changes. Response structure matches the [*Query Video Generation Task* API](/api-reference/video-generation-query).\n\n**Callback `status` values**:\n- `\"processing\"` – Task in progress\n- `\"success\"` – Task completed successfully\n- `\"failed\"` – Task failed\n\n```python\nfrom fastapi import FastAPI, HTTPException, Request\r\nimport json\r\n\r\napp = FastAPI()\r\n\r\n@app.post(\"/get_callback\")\r\nasync def get_callback(request: Request):\r\n    try:\r\n        json_data = await request.json()\r\n        challenge = json_data.get(\"challenge\")\r\n        if challenge is not None:\r\n            # Validation request, echo back challenge\r\n            return {\"challenge\": challenge}\r\n        else:\r\n            # Status update request, handle accordingly\r\n            # {\r\n            #     \"task_id\": \"115334141465231360\",\r\n            #     \"status\": \"success\",\r\n            #     \"file_id\": \"205258526306433\",\r\n            #     \"base_resp\": {\r\n            #         \"status_code\": 0,\r\n            #         \"status_msg\": \"success\"\r\n            #     }\r\n            # }\r\n            return {\"status\": \"success\"}\r\n    except Exception as e:\r\n        raise HTTPException(status_code=500, detail=str(e))\r\n\r\nif __name__ == \"__main__\":\r\n    import uvicorn\r\n    uvicorn.run(\r\n        app,  # Required\r\n        host=\"0.0.0.0\",  # Required\r\n        port=8000,  # Required, port can be customized\r\n        # ssl_keyfile=\"yourname.yourDomainName.com.key\",  # Optional, enable if using SSL\r\n        # ssl_certfile=\"yourname.yourDomainName.com.key\",  # Optional, enable if using SSL\r\n    )\n```"
      example:
        model: MiniMax-Hailuo-2.3
        prompt: A man picks up a book [Pedestal up], then reads [Static shot].
        duration: 6
        resolution: 1080P
    VideoGenerationResp:
      type: object
      properties:
        task_id:
          type: string
          description: The video generation task ID, used for querying status.
        base_resp:
          $ref: '#/components/schemas/BaseResp'
      example:
        task_id: '106916112212032'
        base_resp:
          status_code: 0
          status_msg: success
    BaseResp:
      type: object
      properties:
        status_code:
          type: integer
          description: >-
            The status codes and their meanings are as follows:

            - `0`, Request successful

            - `1002`, Rate limit triggered, please try again later

            - `1004`, Account authentication failed, please check if the API Key
            is correct

            - `1008`, Insufficient account balance

            - `1026`, Sensitive content detected in prompt

            - `2013`, Invalid input parameters, please check if the parameters
            are filled in as required

            - `2049`, Invalid API key


            For more information, please refer to the [Error Code
            Reference](/api-reference/errorcode).  
        status_msg:
          type: string
          description: Status details.
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: >-
        `HTTP: Bearer Auth`

        - Security Scheme Type: http

        - HTTP Authorization Scheme: `Bearer API_key`, can be found in [Account
        Management>API
        Keys](https://platform.minimax.io/user-center/basic-information/interface-key).

````