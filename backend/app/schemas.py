"""Pydantic request/response models. CamelCase to match the QualSched Svelte types.

Never include Qualtrics API tokens or token_ciphertext here.
"""

from pydantic import BaseModel, ConfigDict, Field


class EmailHeader(BaseModel):
    fromEmail: str = "noreply@qualtrics.com"
    fromName: str = "Qualtrics"
    replyToEmail: str = "noreply@qualtrics.com"
    subject: str = "Survey"


class EmbeddedDefaults(BaseModel):
    startDate: str = ""
    surveysScheduled: int = 0
    timeSlots: str = "800,1200,1600,2000"
    contactMethod: str = "sms"
    deleteUnsent: int = 0
    numDays: int = 0
    expireMinutes: int = 60
    logData: str = "[]"
    timeZone: str = "America/Chicago"


class SurveyCopy(BaseModel):
    id: str
    name: str


class Project(BaseModel):
    id: str
    name: str = "New project"
    surveyId: str = ""
    messageId: str = ""
    messageIdEmail: str = ""
    mailingListId: str = ""
    timezone: str = "America/Chicago"
    minutesExpire: int = 60
    emailHeader: EmailHeader = Field(default_factory=EmailHeader)
    embeddedDefaults: EmbeddedDefaults = Field(default_factory=EmbeddedDefaults)
    surveyCopies: list[SurveyCopy] = Field(default_factory=list)
    copiesSourceSurveyId: str = ""


class Account(BaseModel):
    id: str
    name: str = "New account"
    dataCenter: str = ""
    verifyTls: bool = True
    defaultDirectory: str = ""
    libraryId: str = ""
    projects: list[Project] = Field(default_factory=list)


class AppConfig(BaseModel):
    version: int = 1
    accounts: list[Account] = Field(default_factory=list)


class TokenIn(BaseModel):
    token: str


class TestResult(BaseModel):
    ok: bool
    message: str
    directoryCount: int = 0


class IdName(BaseModel):
    id: str
    name: str


class MailingListInfo(BaseModel):
    id: str
    name: str
    contactCount: int | None = None


class MessageInfo(BaseModel):
    id: str
    description: str
    category: str | None = None


class ImportConfirm(BaseModel):
    account: Account
    project: Project
    token: str | None = None
    targetAccountId: str | None = None


class ImportPreview(BaseModel):
    account: Account
    project: Project
    warnings: list[str] = Field(default_factory=list)
    tokenFound: bool = False


class DevLoginIn(BaseModel):
    email: str


class UpdateInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    currentVersion: str
    latestVersion: str
    updateAvailable: bool
    releaseNotes: str = ""
    releaseUrl: str = ""
