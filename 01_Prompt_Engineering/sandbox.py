import docker
import sys

def run_command_in_ubuntu_sandbox(command):
    """
    Runs a shell command inside a temporary Ubuntu Docker container.

    Args:
        command (str): The command to execute in the sandbox.

    Returns:
        str: The stdout from the command execution, or an error message.
    """
    try:
        # Initialize the Docker client from the environment
        client = docker.from_env()

        # Check if Docker is running
        client.ping()

        print(f"Running command in sandbox: '{command}'")
        
        # Run the command in a new, temporary Ubuntu container
        # The container is automatically removed when it's done (`auto_remove=True`)
        container_output = client.containers.run(
            "ubuntu:latest",
            command,
            auto_remove=True,
            stderr=True  # Capture stderr as well
        )
        
        # Decode the output from bytes to a string
        return container_output.decode('utf-8').strip()

    except docker.errors.DockerException as e:
        return f"Error: Docker is not running or not configured correctly. Please start Docker and try again.\nDetails: {e}"
    except docker.errors.ImageNotFound:
        return "Error: The 'ubuntu:latest' image was not found. Please pull it by running: docker pull ubuntu:latest"
    except Exception as e:
        return f"An unexpected error occurred: {e}"

if __name__ == "__main__":
    # Example usage:
    # You can run this script from your terminal like this:
    # python sandbox.py "ls -la /"
    # python sandbox.py "echo 'Hello from the sandbox!'"

    if len(sys.argv) > 1:
        command_to_run = " ".join(sys.argv[1:])
        output = run_command_in_ubuntu_sandbox(command_to_run)
        print("\n--- Sandbox Output ---")
        print(output)
        print("----------------------")
    else:
        print("Usage: python sandbox.py <command_to_run>")
        # Example with a default command if none is provided
        print("\nRunning default example command: 'ls -la /'")
        default_command = "ls -la /"
        output = run_command_in_ubuntu_sandbox(default_command)
        print("\n--- Sandbox Output ---")
        print(output)
        print("----------------------")
