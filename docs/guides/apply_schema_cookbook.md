# Cookbook: Applying Database Schema to Private Cloud SQL (PostgreSQL)

This guide provides step-by-step instructions to apply the `setup_db.py` script (which creates the necessary tables for the AI Marketing System) to your private Cloud SQL PostgreSQL instance named `ai-marketing-db` (with private IP `10.120.0.3`).

**Prerequisites for both methods:**

1.  **`setup_db.py` script:** Ensure you have this script. It was attached to a previous message and its content is also included at the end of this guide for convenience.
2.  **Python 3:** Installed on the machine where you will run the script. (Download: [https://www.python.org/downloads/](https://www.python.org/downloads/))
3.  **psycopg2-binary:** The Python PostgreSQL adapter. Install it using pip: `pip install psycopg2-binary`
4.  **Google Cloud SDK (`gcloud` CLI):** Installed and configured. (Installation: [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install))

---

## Method 1: Using Cloud SQL Auth Proxy on Your Local Machine

This method is suitable if you want to run the script from your local computer. The Cloud SQL Auth Proxy creates a secure local connection to your Cloud SQL instance.

**Steps:**

1.  **Authenticate `gcloud` CLI:**
    Ensure your `gcloud` CLI is authenticated with credentials that have permissions to connect to the Cloud SQL instance. Typically, logging in with your user account is sufficient if that account has the "Cloud SQL Client" role (or broader roles like Editor/Owner) for the project `ai-marketing-system-459423`.
    ```bash
    gcloud auth login
    gcloud auth application-default login
    ```
    Follow the browser prompts to authenticate.

2.  **Get the Cloud SQL Instance Connection Name:**
    You'll need this for the proxy. We previously determined it to be `ai-marketing-system-459423:us-central1:ai-marketing-db`.
    You can verify it with:
    ```bash
    gcloud sql instances describe ai-marketing-db --project=ai-marketing-system-459423 --format="value(connectionName)"
    ```

3.  **Download and Install the Cloud SQL Auth Proxy:**
    *   Instructions and downloads: [https://cloud.google.com/sql/docs/postgres/connect-auth-proxy#install](https://cloud.google.com/sql/docs/postgres/connect-auth-proxy#install)
    *   For Linux (amd64), you can use:
        ```bash
        wget https://dl.google.com/cloudsql/cloud_sql_proxy.linux.amd64 -O cloud_sql_proxy
        chmod +x cloud_sql_proxy
        ```
    *   For Windows or macOS, follow the links above.

4.  **Start the Cloud SQL Auth Proxy:**
    Open a new terminal window and run the proxy. It will run in the foreground and print connection messages.
    Replace `INSTANCE_CONNECTION_NAME` with your actual instance connection name (`ai-marketing-system-459423:us-central1:ai-marketing-db`).
    ```bash
    ./cloud_sql_proxy -instances=INSTANCE_CONNECTION_NAME=tcp:5432
    ```
    For example:
    ```bash
    ./cloud_sql_proxy -instances=ai-marketing-system-459423:us-central1:ai-marketing-db=tcp:5432
    ```
    The proxy will now listen on `127.0.0.1:5432` (localhost, port 5432) and forward connections to your Cloud SQL instance.

5.  **Modify `setup_db.py` for Local Proxy Connection:**
    Open your `setup_db.py` script and change the `DB_HOST` variable to `"127.0.0.1"` (or `"localhost"`) and ensure `DB_PORT` (if you add it) is `5432`.
    ```python
    # Near the top of setup_db.py
    DB_HOST = "127.0.0.1"  # Changed from the private IP
    DB_PORT = 5432 # Default PostgreSQL port, ensure proxy uses this
    DB_NAME = "postgres"  # Or your specific database if you created one other than 'postgres'
    DB_USER = "postgres"  # Your PostgreSQL superuser
    DB_PASSWORD = "supersecretpassword" # The password you set for the 'postgres' user

    # ... rest of the script ...

    # In the main function, ensure the connection uses the port if specified
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT, # Add port here
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=10
    )
    ```

6.  **Run the `setup_db.py` Script:**
    In a *new* terminal window (while the proxy is still running in its own window), navigate to the directory containing `setup_db.py` and run it:
    ```bash
    python3 setup_db.py
    ```
    The script should now connect through the proxy and create the tables.

7.  **Stop the Proxy:**
    Once the script is finished, you can stop the Cloud SQL Auth Proxy by pressing `Ctrl+C` in its terminal window.

---

## Method 2: Running the Script from a GCE VM in the Same VPC

This method is suitable if you have a Compute Engine VM running in the same VPC network as your Cloud SQL instance. This VM can connect directly to the private IP of the Cloud SQL instance.

**Steps:**

1.  **Ensure GCE VM Exists and Has Network Access:**
    *   You need a GCE VM in the `default` VPC network (or whichever network your Cloud SQL instance is peered with) in the `us-central1` region.
    *   The VM needs firewall rules allowing egress traffic to the Cloud SQL instance's private IP (`10.120.0.3`) on TCP port 5432. Often, default VPC rules might allow this, but verify.

2.  **SSH into the GCE VM:**
    Use the `gcloud` CLI or the Cloud Console to SSH into your GCE VM.
    ```bash
    gcloud compute ssh YOUR_VM_NAME --zone=YOUR_VM_ZONE --project=ai-marketing-system-459423
    ```

3.  **Install Prerequisites on the VM:**
    Once on the VM, install Python 3 and the PostgreSQL adapter:
    ```bash
    sudo apt update
    sudo apt install -y python3 python3-pip
    pip3 install psycopg2-binary
    ```

4.  **Copy `setup_db.py` to the VM:**
    You can use `gcloud compute scp` from your local machine to copy the script to the VM:
    ```bash
    gcloud compute scp /path/to/your/local/setup_db.py YOUR_VM_NAME:~ --zone=YOUR_VM_ZONE --project=ai-marketing-system-459423
    ```
    (Replace `/path/to/your/local/setup_db.py` with the actual path on your machine).
    Alternatively, you can manually copy-paste its content into a new file on the VM using a text editor like `nano` or `vim`.

5.  **Ensure `setup_db.py` Uses the Private IP:**
    On the VM, open `setup_db.py` and verify that `DB_HOST` is set to the private IP of your Cloud SQL instance:
    ```python
    # Near the top of setup_db.py
    DB_HOST = "10.120.0.3" # This should be the private IP
    DB_NAME = "postgres"
    DB_USER = "postgres"
    DB_PASSWORD = "supersecretpassword"
    ```

6.  **Run the `setup_db.py` Script on the VM:**
    Navigate to the directory where you placed `setup_db.py` on the VM and run it:
    ```bash
    python3 setup_db.py
    ```
    The script should connect directly to the private IP and create the tables.

---

**Content of `setup_db.py` (for reference):**

```python
import psycopg2
import os

# Modify DB_HOST, DB_PORT (if using proxy) as per the method you choose
DB_HOST = "10.120.0.3"  # For direct connection from GCE VM, or "127.0.0.1" for local proxy
# DB_PORT = 5432 # Uncomment and set if using proxy and it's not default 5432
DB_NAME = "postgres"  # Default database, or a specific one if created
DB_USER = "postgres"  # Default superuser for PostgreSQL
DB_PASSWORD = "supersecretpassword" # The password set during instance creation

create_tables_sql = """
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS businesses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    industry VARCHAR(255),
    intake_data JSONB, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS blueprints (
    id SERIAL PRIMARY KEY,
    business_id INTEGER UNIQUE REFERENCES businesses(id) ON DELETE CASCADE,
    blueprint_name VARCHAR(255) NOT NULL,
    blueprint_data JSONB, 
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS campaigns (
    id SERIAL PRIMARY KEY,
    blueprint_id INTEGER REFERENCES blueprints(id) ON DELETE SET NULL,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    start_date DATE,
    end_date DATE,
    budget DECIMAL(12, 2),
    spend DECIMAL(12, 2) DEFAULT 0.00,
    target_audience TEXT,
    channels JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    email VARCHAR(255),
    phone_number VARCHAR(50),
    status VARCHAR(50) DEFAULT 'new',
    source VARCHAR(255),
    lead_score INTEGER,
    custom_fields JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    blueprint_id INTEGER REFERENCES blueprints(id) ON DELETE SET NULL,
    campaign_id INTEGER REFERENCES campaigns(id) ON DELETE SET NULL,
    lead_id INTEGER REFERENCES leads(id) ON DELETE SET NULL,
    business_id INTEGER REFERENCES businesses(id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    due_date TIMESTAMP WITH TIME ZONE,
    assigned_to_agent_id VARCHAR(255),
    automation_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ai_models (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    version VARCHAR(50),
    type VARCHAR(100),
    config JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value JSONB,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id INTEGER,
    details JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DO $$
DECLARE
    t_name TEXT;
BEGIN
    FOR t_name IN 
        SELECT table_name 
        FROM information_schema.columns 
        WHERE column_name = 'updated_at' AND table_schema = 'public'
    LOOP
        EXECUTE format('CREATE TRIGGER set_timestamp
                        BEFORE UPDATE ON %I
                        FOR EACH ROW
                        EXECUTE PROCEDURE trigger_set_timestamp();', t_name);
    END LOOP;
END;
$$;
"""

def main():
    conn = None
    try:
        print(f"Connecting to PostgreSQL database at {DB_HOST}...")
        conn_params = {
            'host': DB_HOST,
            'dbname': DB_NAME,
            'user': DB_USER,
            'password': DB_PASSWORD,
            'connect_timeout': 10
        }
        # if 'DB_PORT' in globals(): # Check if DB_PORT is defined (for proxy method)
        #     conn_params['port'] = DB_PORT

        conn = psycopg2.connect(**conn_params)
        print("Connected successfully!")
        
        cur = conn.cursor()
        
        print("Creating tables...")
        cur.execute(create_tables_sql)
        conn.commit()
        print("Tables created successfully (or already exist).")
        
        cur.close()
    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        print("Please ensure the Cloud SQL instance is running and accessible.")
        print(f"Host: {DB_HOST}, DB: {DB_NAME}, User: {DB_USER}") # Add Port if used
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
```

Let me know if any of these steps are unclear or if you encounter any issues!

