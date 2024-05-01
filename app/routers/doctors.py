from fastapi import APIRouter, HTTPException, Depends
from app.database.models import user
from app.database.models.patient import PatientDoctor, Patient, Patient_Pydantic
from app.database.models.user import UserRole, User_Pydantic, User
from app.helpers.security import authenticated

router = APIRouter()


@router.get("/doctors", dependencies=[Depends(authenticated())] , response_model=list[User_Pydantic])
async def get_doctors():
    """
        Retrieves a list of doctors with the role set to doctor.

        Returns:
            list[User_Pydantic]: A list of User_Pydantic objects representing the doctors.
        Raises:
            HTTPException: If an error occurs during the retrieval process.
    """
    try:
        doctors = await User.filter(role=UserRole.DOCTOR)
        return doctors
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/doctors/{doctor_id}", dependencies=[Depends(authenticated())], response_model=User_Pydantic)
async def get_doctor(doctor_id: int):
    """
        Retrieves a doctor with the specified doctor_id and role set to doctor.

        Parameters:
            doctor_id (int): The unique identifier of the doctor to retrieve.

        Returns:
            User_Pydantic: A User_Pydantic object representing the doctor.

        Raises:
            HTTPException: If the specified doctor is not found.
    """
    try:
        doctor = await User.get(id=doctor_id, role=UserRole.DOCTOR)
        return doctor
    except Exception as e:
        raise HTTPException(status_code=404, detail="Doctor not found")


@router.get("/doctors/{doctor_id}/assigned-patients", dependencies=[Depends(authenticated())], response_model=list[Patient_Pydantic])
async def get_assigned_patients(doctor_id: int):
    """
        Retrieves a list of patients assigned to a specific doctor based on the provided doctor_id.

        Parameters:
            doctor_id (int): The unique identifier of the doctor to retrieve assigned patients for.

        Returns:
            list[Patient_Pydantic]: A list of Patient_Pydantic objects representing the assigned patients.
        Raises:
            HTTPException: If an error occurs during the retrieval process.
    """
    try:
        assigned_patients = await PatientDoctor.filter(doctor_id=doctor_id)
        patient_ids = [assigned_patient.patient_id for assigned_patient in assigned_patients]
        patients = await Patient.filter(id__in=patient_ids)
        return patients
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))