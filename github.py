import git

repository_url='https://github.com/phonepe/pulse.git'

destination_data= r"data"
git.Repo.clone_from(repository_url,destination_data)

