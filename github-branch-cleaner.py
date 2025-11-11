import marimo

__generated_with = "0.17.6"
app = marimo.App(width="medium")


@app.cell
def _():
    import re
    import requests
    import subprocess

    from requests.exceptions import HTTPError
    return HTTPError, re, requests, subprocess


@app.cell
def _():
    GITHUB_TOKEN = ""
    return (GITHUB_TOKEN,)


@app.cell
def _(GITHUB_TOKEN, HTTPError, requests):
    def get_remote_branches(user, repo):
        """
        Get remote branches from a GitHub repo.
        """

        url = f"https://api.github.com/repos/{user}/{repo}/branches"

        try:
            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
            )

            if response.status_code != 200:
                print(f"Status Code: {response.status_code}")
                return

            branches = response.json()
            branches_names = list(map(lambda x: x["name"], branches))

            return branches_names
        except HTTPError as http_err:
            print(f"HTTP error ocurred: {http_err}")
        except Exception as err:
            print(f"Other error ocurred: {err}")
    return


@app.cell
def _(re):
    def extract_repo(text):
        """
        Extract the repo `[USER]/[REPO]` from a text that represents the output of the `git remote` command
        """

        regex = r"git@github.com:([\w_-]+)/([\w_-]+)"

        result = re.search(regex, text)

        if not result:
            return None

        user = result.group(1)
        repo = result.group(2)

        return f"{user}/{repo}"
    return (extract_repo,)


@app.cell
def _(extract_repo, subprocess):
    def get_repo_from_local(local_repo_path):
        """
        Get the remote repo `[USER]/[REPO]` from a local repository
        """

        result = subprocess.run(
            ["git", "remote", "--verbose"],
            cwd=local_repo_path,
            capture_output=True
        )

        if result.returncode != 0:
            err = result.stderr.decode("utf-8")

            print(f"An error happened {err}")
            return None

        output = result.stdout.decode("utf-8")

        return extract_repo(output)
    return (get_repo_from_local,)


@app.cell
def _(re):
    def extract_branches(text):
        """
        Extract branches names from a text that represents the output of the `git branch` command
        """

        regex = r"([\w\-_]+)"

        result = re.findall(regex, text)

        if not result:
            return None

        return result
    return (extract_branches,)


@app.cell
def _(extract_branches, subprocess):
    def get_local_branches(local_repo_path):
        """
        Get the branches names from a local repository
        """

        result = subprocess.run(
            ["git", "--no-pager", "branch"],
            cwd=local_repo_path,
            capture_output=True
        )

        if result.returncode != 0:
            err = result.stderr.decode("utf-8")

            print(f"An error happened {err}")
            return None

        output = result.stdout.decode("utf-8")

        return extract_branches(output)
    return (get_local_branches,)


@app.cell
def _(GITHUB_TOKEN, HTTPError, requests):
    def get_remote_branch(repo, branch_name):
        """
        Get information for a remote branch
        """

        try:
            url = f"https://api.github.com/repos/{repo}/branches/{branch_name}"

            response = requests.get(
                url,
                headers={"Authorization": f"Bearer {GITHUB_TOKEN}"}
            )

            if response.status_code != 200:
                return None

            return response.json()
        except HTTPError as http_err:
            print(f"HTTP error ocurred: {http_err}")
        except Exception as err:
            print(f"Other error ocurred: {err}")
    return (get_remote_branch,)


@app.cell
def _(subprocess):
    def delete_local_branch(local_repo_path, branch):
        """
        Delete (by forcing) a local branch
        """

        result = subprocess.run(
            ["git", "branch", "-D", branch],
            cwd=local_repo_path,
            capture_output=True
        )

        if result.returncode != 0:
            err = result.stderr.decode("utf-8")

            print(f"An error happened {err}")
            return False

        return True
    return (delete_local_branch,)


@app.cell
def _(
    delete_local_branch,
    get_local_branches,
    get_remote_branch,
    get_repo_from_local,
):
    # Clean Up Branches
    local_repo_path = ""

    remote_repo = get_repo_from_local(local_repo_path)
    local_branches = get_local_branches(local_repo_path)

    for branch_name in local_branches:
        branch = get_remote_branch(remote_repo, branch_name)

        if not branch:
            delete_local_branch(local_repo_path, branch_name)
            print(f"Branch {branch_name} deleted")
        else:
            print(f"Branch {branch_name} safe")
    return


if __name__ == "__main__":
    app.run()
