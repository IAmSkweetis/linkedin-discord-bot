import datetime
import uuid
from typing import List

from linkedin_jobs_scraper.filters.filters import ExperienceLevelFilters
from pydantic.alias_generators import to_camel
from sqlalchemy.types import BIGINT
from sqlmodel import Field, Relationship, SQLModel


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
    experience: ExperienceLevelFilters = Field(
        default=ExperienceLevelFilters.MID_SENIOR, title="Filter for experience level"
    )
    creator_discord_id: int = Field(..., title="Discord ID of the creator", sa_type=BIGINT)
    creation_date: datetime.datetime = Field(
        default=datetime.datetime.now(datetime.timezone.utc), title="Creation date of the job query"
    )


class JobQuery(JobQueryBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    jobs: List["Job"] = Relationship(back_populates="job_query")


class Job(BaseModel, table=True):
    job_id: int = Field(
        ...,
        title="Unique identifier for the job. Also correlates to the LinkedIn job ID.",
        primary_key=True,
        sa_type=BIGINT,
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

    job_query_id: uuid.UUID | None = Field(
        default=None, foreign_key="jobquery.id", title="ID of the job query"
    )
    job_query: JobQuery | None = Relationship(back_populates="jobs")
