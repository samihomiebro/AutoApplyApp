from applicationAbstract import Application
from candidateProfile import CandidateProfile, ChatGPT, Resume
from jobBuilderLinkedin import JobBuilder, JobParser, Job
from gmail import Gmail
import json
import os
from deprecated import deprecated

class EmailApplication(Application):
    def __init__(self, candidate_profile: CandidateProfile, jobs: list[Job]):
        self.candidate_profile = candidate_profile
        self.jobs = jobs
        self.type = 'Email'
        self.candidate_experiences= self.candidate_profile.resume.extract_experience_section()
        self.candidate_educations= self.candidate_profile.resume.extract_education_section()
        self.candidate_infos= self.candidate_profile.resume.extract_info_section()

    def ApplyForJob(self, job: Job):
        print(f"sending email application for {job.job_title} at {job.company_name} in {job.job_location}")
        #TODO: put threadpool if email is a list
        gmail = Gmail('jobApp/secrets/credentials.json', 'jobApp/secrets/token.json' )
        # as we have a list of possible emails
        for email in job.company_email:
            status = gmail.send_email_with_attachments(f'{self.candidate_profile.email}',f'{email}',  f'job application as {job.job_title} at {job.company_name} in {job.job_location}', self.generateApplicationTemplate(job), [self.candidate_profile.resume.file_path])
            if status:
                job.setJobApplied(True) # applied for job
    
    def ApplyForAll(self):
        return super().ApplyForAll()

    # generate application email specific for job: use ai to generate 
    @deprecated(reason="generate application email deprecated, use generateApplicationTemplate instead")
    def generateApplicationEmail(self, job:Job):
        query = f"create a job application email draft for the job {job.job_title} at {job.company_name} in {job.job_location} to the hiring manager. \
        use my personal infos: {self.candidate_infos} , experiences: {self.candidate_experiences} and educations: {self.candidate_educations} to highlight my worth\
        here is the job description to apply for: {job.job_description}. close the draft by leaving my contact details. ignore the adress and driving licence."
        chatgpt = ChatGPT("jobApp/secrets/openai.json")
        email_tosend = chatgpt.ask(query)
        return email_tosend
    
    # generate application email as a template for all: create one template with ai
    def generateApplicationTemplate(self, job:Job,  output_file:str='jobApp/data/email_draft_template.json')-> str:
        email_data = {
        "job_title": job.job_title,
        "company": job.company_name,
        "fullname": self.candidate_profile.firstname +" "+ self.candidate_profile.lastname,
        "phone_number": self.candidate_profile.phone_number
    }
        try:
            with open(output_file, "r") as f:
                template = f.read()
            #print(template.format(**email_data))
            return (template.format(**email_data))
        except FileNotFoundError:
            print("The file does not exist.")

        query = f"create a job application email draft as {'{job_title}'} at {'{company}'} to the hiring manager.\
        highlight the experiences: {self.candidate_experiences} and educations: {self.candidate_educations} \
        sincerely, {'{fullname}'} {'{phone_number}'}"
        chatgpt = ChatGPT("jobApp/secrets/openai.json")
        #print(f"query: {query}")
        template = chatgpt.ask(query)
        with open(output_file, "w") as f:
            json.dump(template, f)
        return template.format(**email_data)

if __name__ == '__main__':
    candidate = CandidateProfile(resume_path='jobApp/data/zayneb_dhieb_resume_english.pdf', firstname="zayneb", lastname="dhieb", email="dhiebzayneb89@gmail.com", phone_number="+21620094923")
    jobs = [Job(1, None, "recruiting specialist", "terrNova","Berlin", "one day ago", "as recruiting specialist you will help us achieve our goals", company_email="sami.dhiab.x@gmail.com")]
    emailApply = EmailApplication(candidate, jobs)
    #emailDarft = emailApply.generateApplicationTemplate(jobs[0],'jobApp/data/email_draft_template.json')
    emailApply.ApplyForJob(jobs[0])