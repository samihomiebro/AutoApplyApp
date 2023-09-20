from ..email.emailApplicationBuilder import EmailApplicationBuilder
from ..easyApply.easyApplicationBuilder import EasyApplyApplicationBuilder
from ..externalApply.directApplicationBuilder import DirectApplicationBuilder


class ApplicationDirector:
    def __init__(self):
        self.builder = None

    def construct_application(self, candidate_profile, jobs='jobApp/data/jobs.csv', application_type= 'Email' or 'Easy Apply' or 'Direct'):
        if application_type == 'Email':
            self.builder = EmailApplicationBuilder()
        elif application_type == 'Easy Apply':
            self.builder = EasyApplyApplicationBuilder()
        elif application_type == 'Direct':
            self.builder = DirectApplicationBuilder()
        else:
            raise ValueError('Invalid application type')

        self.builder.set_candidate_profile(candidate_profile)
        self.builder.set_jobs(jobs)
        return self.builder.build_application()

if __name__ == '__main__':

    pass
    