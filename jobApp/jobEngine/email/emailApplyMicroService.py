from applicationDirector import ApplicationDirector
from candidateProfile import CandidateProfile

# TODO Move all paths required for a service  to a config file
    
class EmailApplyMicroService:

    def __init__(self, service_name="email apply", csv_jobs='jobApp/data/jobs.csv'):
        self.name = service_name
        print(f"initialising {self.name} microservice..")
        candidate = CandidateProfile(resume_path='jobApp/data/first_last_resume_english.pdf', 
                                     firstname="first", lastname="last", 
                                     email= "firstdhiab89@gmail.com",   #"email@gmail.com", 
                                     phone_number="+phone")
        appDirector = ApplicationDirector()
        self.emailapp= appDirector.construct_application(candidate_profile=candidate, jobs=csv_jobs, application_type='Email')

    def run_service(self):
        print(f"running {self.name} microservice..")
        self.emailapp.ApplyForAll()

if __name__ == '__main__':
    import sys
    args = sys.argv
    csv_jobs = ""
    csv_jobs = ""
    # get the csv links
    if args[1] :
        csv_jobs= args[1]
        print(f"csv jobs file: {csv_jobs}")
        jlink = EmailApplyMicroService(csv_jobs=csv_jobs)
        jlink.run_service()
    else:
        jlink = EmailApplyMicroService()
        jlink.run_service()