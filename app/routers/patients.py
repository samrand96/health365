from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from tortoise.exceptions import *
from app.database.models.patient import Patient_Pydantic, Patient, MedicalRecord, MedicalRecord_Pydantic, \
    MedicalRecordIn_Pydantic, PatientIn_Pydantic, PatientDoctor, PatientDoctor_Pydantic, Gender
from app.helpers.security import has_permission, get_current_user, authenticated
from app.database.models.user import UserRole, User, User_Pydantic
from app.routers.websocket import send_notification_to_user

router = APIRouter()


@router.get("/patients", dependencies=[Depends(authenticated())] , response_model=list[Patient_Pydantic])
async def get_patients():
    """
        Retrieves a list of all patients from the database.

        Parameters:
            No parameters required.

        Returns:
            A list of Patient_Pydantic objects representing the patients.

        Raises:
            HTTPException with status code 500 and error detail if an exception occurs during retrieval.
    """
    try:
        patients = await Patient.all()
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/patients", dependencies=[Depends(authenticated())] , response_model=Patient_Pydantic)
async def create_patient(patient: PatientIn_Pydantic, user: User_Pydantic = Depends(get_current_user)):
    """
        Creates a new patient based on the provided patient data and the authenticated user.

        Parameters:
            - patient (PatientIn_Pydantic): The data of the new patient.
            - user (User_Pydantic): The authenticated user creating the patient.

        Returns:
            - Patient_Pydantic: The newly created patient information.

        Raises:
            - HTTPException: If the provided gender is invalid or if the data provided is invalid.
    """
    try:
        if patient.gender.strip().lower() not in [member.name.lower() for member in Gender]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid gender "
            )
        new_patient = await Patient.create(**patient.dict(exclude_unset=True))
        return new_patient
    except ValidationError as e:
        raise HTTPException(status_code=500, detail=str("The data provided is invalid"))


@router.get("/patients/{patient_id}", dependencies=[Depends(authenticated())], response_model=Patient_Pydantic)
async def get_patient(patient_id: int):
    """
        Gets a patient based on the provided patient_id.

        Parameters:
            - patient_id (int): The ID of the patient to retrieve.

        Returns:
            - Patient_Pydantic: The patient information.

        Raises:
            - HTTPException: If the specified patient is not found.
    """
    try:
        patient = await Patient.get(id=patient_id)
        return patient
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.put("/patients/{patient_id}", dependencies=[Depends(authenticated())], response_model=Patient_Pydantic)
async def update_patient(patient_id: int, patient: PatientIn_Pydantic):
    """
        Updates a patient's information based on the provided patient_id and new data.

        Parameters:
            - patient_id (int): The ID of the patient to update.
            - patient (PatientIn_Pydantic): The new data for the patient.

        Returns:
            - Patient_Pydantic: The updated patient information.

        Raises:
            - HTTPException: If the specified patient is not found.
    """
    try:
        existing_patient = await Patient.get(id=patient_id)
        await existing_patient.update_from_dict(patient.dict(exclude_unset=True))
        return await Patient_Pydantic.from_tortoise_orm(existing_patient)
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.delete("/patients/{patient_id}", dependencies=[Depends(authenticated())])
async def delete_patient(patient_id: int):
    """
        Deletes a patient based on the provided patient_id.

        Parameters:
            - patient_id (int): The ID of the patient to be deleted.

        Returns:
            - dict: A message indicating the success of the deletion.

        Raises:
            - HTTPException: If the patient is not found.
    """
    try:
        patient = await Patient.get(id=patient_id)
        await patient.delete()
        return {"message": "Patient deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.post("/patients/{patient_id}/assign-doctor/{doctor_id}", dependencies=[Depends(authenticated())], response_model=PatientDoctor_Pydantic)
async def assign_doctor_to_patient(patient_id: int, doctor_id: int, user: User_Pydantic = Depends(get_current_user)):
    """
        Assigns a doctor to a patient based on the provided patient_id and doctor_id.

        Parameters:
            - patient_id (int): The ID of the patient.
            - doctor_id (int): The ID of the doctor to assign to the patient.
            - user (User_Pydantic, optional): The user attempting to assign the doctor.

        Returns:
            - PatientDoctor_Pydantic: The assignment details.

        Raises:
            - HTTPException: If the doctor is already assigned to the patient or if an error occurs during the assignment process.
    """
    try:
        patient = await Patient.get(id=patient_id)
        existing_assignment = await PatientDoctor.filter(patient=patient, doctor_id=doctor_id)
        if existing_assignment:
            raise HTTPException(status_code=400, detail="Doctor is already assigned to this patient")
        user = await User.get(id=doctor_id, role=UserRole.DOCTOR)
        assignment = await PatientDoctor.create(patient=patient, doctor_id=doctor_id)

        message = f"New patient assigned from: {user.email}"
        await send_notification_to_user(user_id=int(doctor_id), message=message)

        return assignment
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))



@router.get("/patients/{patient_id}/assigned-doctors", dependencies=[Depends(authenticated())], response_model=list[User_Pydantic])
async def get_assigned_doctors(patient_id: int):
    """
        Attempts to get the list of doctors assigned to a specific patient based on the provided patient_id.

        Parameters:
            - patient_id (int): The ID of the patient for whom assigned doctors are requested.

        Returns:
            - list[User_Pydantic]: A list of User_Pydantic objects representing the assigned doctors.

        Raises:
            - HTTPException: If the patient with the given patient_id is not found.
    """
    try:
        assigned_doctors = await PatientDoctor.filter(patient_id=patient_id)
        doctor_ids = [assigned_doctor.doctor_id for assigned_doctor in assigned_doctors]
        doctors = await User.filter(id__in=doctor_ids)
        return doctors
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail=str("Patient not found"))


@router.delete("/patients/{patient_id}/unassign-doctor/{doctor_id}", dependencies=[Depends(authenticated())])
async def unassign_doctor_from_patient(patient_id: int, doctor_id: int):
    """
        Attempts to unassign a doctor from a patient based on their IDs.

        Parameters:
            - patient_id (int): The ID of the patient.
            - doctor_id (int): The ID of the doctor being unassigned.

        Returns:
            - dict: A message indicating the success of the unassignment.

        Raises:
            - HTTPException: If the doctor-patient assignment does not exist.
    """
    try:
        assignment = await PatientDoctor.get(patient_id=patient_id, doctor_id=doctor_id)
        await assignment.delete()
        return {"message": "Doctor unassigned successfully"}
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail=str("They were never assigned"))


@router.get("/patients/{patient_id}/medical-information", dependencies=[Depends(has_permission(UserRole.DOCTOR))], response_model=list[MedicalRecord_Pydantic])
async def get_patient_medical_information(patient_id: int, user: User_Pydantic = Depends(get_current_user)):
    """
    Gets the medical information of a patient based on the provided patient_id and user.

    Parameters:
        - patient_id (int): The ID of the patient.
        - user (User_Pydantic, optional): The user requesting the patient's medical information.

    Returns:
        - list[MedicalRecord_Pydantic]: The medical records related to the patient.

    Raises:
        - HTTPException: If the patient is not found or the user does not have permission to access the information.
    """
    try:
        # Check whether the patient is assigned to current doctor or the doctor has right to see the patient
        # information for patient privacy
        try:
            doctor = await User.get(id=user.id, role=UserRole.DOCTOR)
            patient = await Patient.get(id=patient_id)
            await PatientDoctor.get(patient=patient, doctor=doctor)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="You have no permission to see this patient information")
        medical_records = await MedicalRecord.filter(patient=patient)
        return medical_records
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail="Patient not found")


@router.post("/patients/{patient_id}/medical-information", dependencies=[Depends(authenticated())], response_model=MedicalRecord_Pydantic)
async def create_medical_record(patient_id: int, medical_record: MedicalRecordIn_Pydantic, user: User_Pydantic = Depends(get_current_user)):
    """
        Creates a new medical record for a patient.

        Parameters:
            - patient_id (int): The ID of the patient.
            - medical_record (MedicalRecordIn_Pydantic): The medical record data to create.
            - user (User_Pydantic, optional): The user attempting to create the record.

        Returns:
            - MedicalRecord_Pydantic: The newly created medical record.

        Raises:
            - HTTPException: If the patient is not found, or the user has no permission to create a medical record.
        """
    try:
        # Check whether the patient is assigned to current doctor or the doctor has right to create medical record
        # for the patient
        try:
            doctor = await User.get(id=user.id, role=UserRole.DOCTOR)
            patient = await Patient.get(id=patient_id)
            await PatientDoctor.get(patient=patient, doctor=doctor)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="You have no permission to create medical record for this "
                                                        "patient")
        new_medical_record = await MedicalRecord.create(patient=patient, doctor=doctor,
                                                        **medical_record.dict(exclude_unset=True))
        return new_medical_record
    except DoesNotExist as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/patients/{patient_id}/medical-information/{record_id}", dependencies=[Depends(authenticated())], response_model=MedicalRecord_Pydantic)
async def update_medical_record(patient_id: int, record_id: int, medical_record: MedicalRecordIn_Pydantic, user: User_Pydantic = Depends(get_current_user)):
    """
        Updates a medical record for a patient.

        Parameters:
            - patient_id (int): The ID of the patient.
            - record_id (int): The ID of the medical record to update.
            - medical_record (MedicalRecordIn_Pydantic): The updated medical record data.
            - user (User_Pydantic, optional): The user attempting to update the record.

        Returns:
            - MedicalRecord_Pydantic: The updated medical record.

        Raises:
            - HTTPException: If the patient or medical record is not found, or the user has no permission to update the record.
        """
    try:
        # Check whether the patient is assigned to current doctor or the doctor has right to update medical record
        # for the patient
        try:
            doctor = await User.get(id=user.id, role=UserRole.DOCTOR)
            patient = await Patient.get(id=patient_id)
            await PatientDoctor.get(patient=patient, doctor=doctor)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="You have no permission to update medical record for this "
                                                        "patient")
        record = await MedicalRecord.get(id=record_id, patient=patient)
        await record.update_from_dict(medical_record.dict(exclude_unset=True))
        return await MedicalRecord_Pydantic.from_tortoise_orm(record)
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail="Patient or medical record not found")


@router.delete("/patients/{patient_id}/medical-information/{record_id}", dependencies=[Depends(authenticated())])
async def delete_medical_record(patient_id: int, record_id: int, user: User_Pydantic = Depends(get_current_user)):
    """
        Deletes a medical record for a patient.

        Parameters:
            - patient_id (int): The ID of the patient.
            - record_id (int): The ID of the medical record to delete.
            - user (User_Pydantic, optional): The user attempting to delete the record.

        Returns:
            - dict: A message indicating the success of the deletion.

        Raises:
            - HTTPException: If the patient or medical record is not found, or the user has no permission to delete the record.
        """
    try:
        # Check whether the patient is assigned to current doctor or the doctor has right to delete medical record
        # for the patient
        try:
            doctor = await User.get(id=user.id, role=UserRole.DOCTOR)
            patient = await Patient.get(id=patient_id)
            await PatientDoctor.get(patient=patient, doctor=doctor)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="You have no permission to delete medical record for this "
                                                        "patient")
        record = await MedicalRecord.get(id=record_id, patient=patient)
        await record.delete()
        return {"message": "Medical record deleted successfully"}
    except DoesNotExist as e:
        raise HTTPException(status_code=404, detail="Patient or medical record not found")
