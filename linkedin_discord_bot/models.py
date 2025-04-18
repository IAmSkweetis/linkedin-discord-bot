import uuid

from linkedin_jobs_scraper.filters.filters import ExperienceLevelFilters
from pydantic.alias_generators import to_camel
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True


class JobQueryBase(BaseModel):
    query: str = Field(..., title="Search query for the job listing")
    locations: str = Field(..., title="List of locations to search for jobs")
    games_only: bool = Field(
        default=False,
        title="Filter for game-related jobs",
        description="If true, only game-related jobs will be returned",
    )
    remote_only: bool = Field(
        default=False,
        title="Filter for on-site or remote jobs",
        description="If true, only remote jobs will be returned",
    )
    experience: ExperienceLevelFilters = Field(..., title="Filter for experience level")


class JobQuery(JobQueryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)


class Job(BaseModel, table=True):
    job_id: int = Field(..., title="Unique identifier for the job", primary_key=True)
    query_id: uuid.UUID | None = Field(
        default=None, foreign_key="jobquery.id", title="ID of the job query"
    )
    location: str = Field(..., title="Location of the job listing")
    link: str = Field(..., title="URL to the job listing")
    apply_link: str | None = Field(default=None, title="URL to apply for the job")
    title: str = Field(..., title="Title of the job")
    company: str = Field(..., title="Company offering the job")
    company_link: str | None = Field(default=None, title="URL to the company's LinkedIn page")
    company_img_link: str | None = Field(default=None, title="URL to the company's logo")
    place: str = Field(..., title="Location of the job")
    description: str = Field(..., title="Description of the job")
    description_html: str = Field(..., title="HTML description of the job")
    date: str = Field(..., title="Date the job was posted")
    date_text: str = Field(..., title="Text representation of the date")
