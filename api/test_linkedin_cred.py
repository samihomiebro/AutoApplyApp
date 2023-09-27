# api/job_search.py
from fastapi import APIRouter, HTTPException
from models.request_models import PlatformCredRequest
from appCore import appCreatorLinkedin, LoginException
from models.response_models import PlatformCredResponse
import logging

router = APIRouter()


@router.post("/api/testPlatformCredRequest/")
def testPlatformCredRequest(userCred: PlatformCredRequest):
    try:
        logging.info(f"request body: {userCred}")

        linkedinLoginData = {
            "user":{
                "email": userCred.model_dump().get("email"),
                "password": userCred.model_dump().get("password"),
                "_owner": userCred.model_dump().get("_owner"),
                "field_id": userCred.model_dump().get("field_id"),
                "created_date": userCred.model_dump().get("created_date"),
            }
        }
        PlatformCredRequestApp = appCreatorLinkedin(linkedinLoginData)
        verified = PlatformCredRequestApp.tryCredentialsLinkedin()
        if verified:
            return PlatformCredResponse(
                    message="Users Credentials verified successfully",
                    data={"data": "verified"}, 
                    status="ok"
                )
        else:
            return PlatformCredResponse(
                    message="Users Credentials could not be verified",
                    data={"data": "not verified"}, 
                    status="error"
                )   
        #raise CustomException("login failed")
    except LoginException as loginError:
        logging.error("loginError occurred: %s", loginError)
        raise HTTPException(status_code=400, detail=str(loginError))
    except Exception as E:
        logging.error("Exception occured: %s", E)
        raise HTTPException(status_code=500, detail=str(E))