from application.applicationBuilderAbstract import ApplicationBuilder
from easyApplyApplication import EasyApplyApplication

class EasyApplyApplicationBuilder(ApplicationBuilder):
    def __init__(self):
        self.candidate_profile = None
        self.jobs = None

    def set_candidate_profile(self, profile):
        self.candidate_profile = profile

    def set_jobs(self, jobs):
        self.jobs = jobs

    def build_application(self):
        return EasyApplyApplication(self.candidate_profile, self.jobs)



