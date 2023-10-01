from ..email.emailApplicationBuilder import EmailApplicationBuilder
from ..easyApply.easyApplicationBuilder import EasyApplyApplicationBuilder
from ..externalApply.directApplicationBuilder import DirectApplicationBuilder
from .applicationAbstract import Application
import json
from ..user.candidateProfile import CandidateProfile
from ..config.config import BaseConfig , UserConfig, AppConfig

class ApplicationDirector:
    def __init__(self, linkedinConfig, application_type='Easy Apply'):
        self.builder = None
        self.linkedinConfig = linkedinConfig
        self.candidate = self.createCandidatePofile(linkedinConfig)
        self.csv_jobs_file = self.deductUserInCsvJobs(linkedinConfig)
    
    def construct_application(self,  application_type= 'Email' or 'Easy Apply' or 'Direct'):
        if application_type == 'Email':
            self.builder = EmailApplicationBuilder()
        elif application_type == 'Easy Apply':
            self.builder = EasyApplyApplicationBuilder()
        elif application_type == 'Direct':
            self.builder = DirectApplicationBuilder()
        else:
            raise ValueError('Invalid application type')

        self.builder.set_candidate_profile(self.candidate)
        self.builder.set_jobs_file(self.csv_jobs_file)
        self.builder.set_linkedin_data(self.linkedinConfig)
        return self.builder.build_application()

    ######## utility code: place under another utils module #####
    def createCandidatePofile(self, incomingData):
        json_data = self.loadIncomingDataAsJson(incomingData)
        # User data
        user_data:dict = json_data.get('user')
        email = user_data.get("email")
        self.field_id = user_data.get('field_id')
        # candidate data
        candidate_data:dict = json_data.get("candidate")
        firstname = candidate_data.get('firstname')
        lastname = candidate_data.get('lastname')
        resume = candidate_data.get('resume')
        phone_number = candidate_data.get('phone_number')
        address = candidate_data.get('address')
        limit = candidate_data.get('limit')
        return CandidateProfile(resume_path=resume, 
                                     firstname=firstname, 
                                     lastname=lastname, 
                                     email=email,  
                                     phone_number=phone_number, 
                                     limit=limit, 
                                     address=address )
    
    def deductUserInCsvJobs(self, incomingData):
        json_data = self.loadIncomingDataAsJson(incomingData)
        # User data
        job:dict = json_data.get("search_params")
        job_title = job.get('job')
        location = job.get('location')
        return UserConfig.get_jobs_file_path(job_title=job_title, job_location=location,field_id= self.field_id)
        #return self.getUserSearchJobsCsv(csv_path=csv_path, job_title=job_title, job_location=location, field_id=self.field_id)
    
    def replace_spaces_and_commas_with_underscores(self, input_string:str):
        # Replace spaces and commas with underscores
        modified_string = input_string.replace(' ', '_').replace(',', '_')
        return modified_string
    
    def getUserSearchJobsCsv(self, csv_path, job_title, job_location, field_id):
        job_title = self.replace_spaces_and_commas_with_underscores(job_title)
        location = self.replace_spaces_and_commas_with_underscores(job_location)
        csv_extension = ".csv"
        jobs_path = "/jobs"
        file = csv_path+jobs_path+"_"+job_title+"_"+location+"_"+field_id+csv_extension # maybe owner id is needed here
        return file

    def loadIncomingDataAsJson(self, incomingData):
        #print("incoming Data: ", incomingData)
        # load actual user data   
        if isinstance(incomingData, str):
            # If incomingData is a string, assume it's a file path
            try:
                with open(incomingData, 'r') as file:
                    json_data = json.load(file)
            except FileNotFoundError:
                raise FileNotFoundError("File not found")
        elif isinstance(incomingData, dict):
            # If incomingData is a dictionary, assume it's a JSON object
            json_data = incomingData
        else:
            raise ValueError("Invalid incomingData type")
        return json_data





if __name__ == '__main__':

    pass
    
