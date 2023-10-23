from app.controllers.appliance_controller import add_appliance

# test_add_appliance.py

# Sample data
user_id = "sample_user_id"
name = "Sample Appliance"
cloud_id = "sample_cloud_id"
type = "COOLER"  # Assuming this is a valid ApplianceType

# Call the function
response, status_code = add_appliance(user_id, name, cloud_id, type)

# Print the response
print(response, status_code)
