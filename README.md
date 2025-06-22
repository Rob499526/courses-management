docker-compose up -d
lt --port 8000 --subdomain coursemanagement
poetry run uvicorn app.main:app --reload
PYTEST_ASYNCIO_MODE=auto poetry run pytest tests/ -v

# Courses Management API

A FastAPI-based application for managing courses and user enrollments.

## Testing

The project includes comprehensive test coverage for the courses CRUD operations. Tests are located in the `tests` directory and can be run using pytest.

### Test Coverage

The test suite covers the following aspects:

1. **Course Creation**
   - Creating a new course with valid data
   - Validation of required fields
   - Error handling for invalid input

2. **Course Retrieval**
   - Listing all courses
   - Retrieving a specific course by ID
   - Handling non-existent courses

3. **Course Update**
   - Updating course details
   - Validation of updates
   - Error handling for non-existent courses

4. **Course Deletion**
   - Deleting a course
   - Verifying deletion from database
   - Error handling for non-existent courses

5. **User Enrollment**
   - Enrolling a user in a course
   - Preventing duplicate enrollments
   - Verifying enrollment status

### Running Tests

To run the tests, you need to have pytest installed. You can install it using:

```bash
pip install pytest pytest-asyncio
```

Then run the tests with:

```bash
pytest tests/ -v
```

The `-v` flag provides verbose output showing each test case as it runs.

### Test Organization

The tests are organized into two main files:

1. `tests/conftest.py`: Contains test fixtures and setup code
   - Database setup and teardown
   - Test user and course fixtures
   - Test client setup

2. `tests/test_courses.py`: Contains all course-related test cases
   - Each test is marked with `@pytest.mark.asyncio` for async operations
   - Tests are organized by functionality (create, read, update, delete)
   - Includes both positive and negative test cases

### Test Dependencies

The tests require the following dependencies:
- pytest
- pytest-asyncio
- httpx (for test client)
- SQLAlchemy (for database operations)

### Test Environment

The tests use an in-memory database for testing, ensuring that:
- Each test runs in isolation
- Database is reset between tests
- No external dependencies are required

### Test Best Practices

The test suite follows these best practices:
- Each test is independent and self-contained
- Clear test names that describe the functionality
- Proper error handling verification
- Database state verification
- Comprehensive coverage of edge cases


docker-compose up -d
lt --port 8000 --subdomain coursemanagement
poetry run uvicorn app.main:app --reload
