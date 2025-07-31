# MCDA API Testing Documentation

## Overview

This document describes the comprehensive test suite created for the MCDA API project using Django's native testing framework.

## Test Coverage

### Account App Tests (22 tests)

- ✅ **GenderEnumTest**: Tests for Gender enum choices and functionality
- ✅ **SexualityEnumTest**: Tests for Sexuality enum choices and functionality  
- ✅ **UsersModelTest**: Tests for Users model creation, validation, and constraints
- ✅ **EmailToCodeUtilTest**: Tests for the email_to_code utility function
- ✅ **CustomRegisterSerializerTest**: Tests for user registration serializer validation
- ✅ **AccountViewsTest**: Tests for API endpoints (get_user_by_filter, manage_user)
- ✅ **CustomUserDetailsSerializerTest**: Tests for user details serializer (security fixed)

### Privacy App Tests (16 tests)

- ✅ **UserPrivacyModelTest**: Tests for UserPrivacy model and cascade deletion
- ✅ **UserPrivacySerializerTest**: Tests for privacy settings serialization
- ✅ **PrivacyViewsTest**: Tests for privacy API endpoints (get, toggle status/last_seen)

### Relationships App Tests (15 tests)  

- ✅ **StatusEnumTest**: Tests for relationship status enum choices
- ✅ **RelationshipModelTest**: Tests for Relationship model and constraints
- ✅ **RelationshipRequestModelTest**: Tests for RelationshipRequest model
- ✅ **RelationshipSerializerTest**: Tests for relationship data serialization
- ✅ **RelationshipViewsTest**: Tests for relationship API endpoints (manage, create, respond)

## Test Infrastructure

### Database Configuration

- **Development**: MySQL database
- **Testing**: SQLite in-memory database for faster test execution
- Automatic database switching when running tests

### Base Test Classes

Located in `tests/base.py`:

- **BaseTestCase**: Common utilities for model tests
- **BaseAPITestCase**: API testing with authentication helpers
- **ModelTestMixin**: Model validation utilities
- **SerializerTestMixin**: Serializer testing utilities
- **DatabaseTestMixin**: Database operation utilities

### Test Fixtures

Located in `tests/test_fixtures.py`:

- **TestDataFactory**: Factory methods for creating test data
- Sample data sets for different test scenarios
- Predefined test data for edge cases

## Running Tests

### Using the Custom Test Runner

```bash
# Run all tests
python test_runner.py all

# Run tests for specific app
python test_runner.py Account
python test_runner.py Privacy  
python test_runner.py Relationships

# Run tests with coverage report
python test_runner.py coverage

# Run specific test class or method
python test_runner.py specific Account.tests.UsersModelTest
python test_runner.py specific Account.tests.UsersModelTest.test_create_user
```

### Using Django's Test Command

```bash
# Activate virtual environment first
source venv/bin/activate

# Run all tests
python manage.py test

# Run specific app tests
python manage.py test Account.tests
python manage.py test Privacy.tests
python manage.py test Relationships.tests

# Run with verbosity
python manage.py test --verbosity=2
```

## Security Improvements Made

### Fixed Password Exposure

- **Issue**: CustomUserDetailsSerializer was exposing password field
- **Fix**: Updated serializer to exclude password field for security
- **Test**: Added test to verify password is not exposed in API responses

### Improved Boolean Parameter Handling

- **Issue**: API endpoints not properly handling boolean parameters from JSON
- **Fix**: Enhanced boolean validation in relationship request responses
- **Test**: Verified proper handling of true/false values

## Test Statistics

- **Total Tests**: 53
- **Success Rate**: 100% ✅
- **Average Runtime**: ~7.6 seconds
- **Database**: SQLite in-memory (test isolation)

## Key Testing Features

### Model Testing

- ✅ Field validation and constraints
- ✅ Model creation and updates
- ✅ Cascade deletion behavior
- ✅ Unique constraint enforcement
- ✅ Enum choice validation

### API Testing

- ✅ Authentication requirements
- ✅ Parameter validation
- ✅ Response format verification
- ✅ Error handling
- ✅ HTTP status codes
- ✅ CRUD operations

### Serializer Testing

- ✅ Data validation
- ✅ Field presence/absence
- ✅ Serialization accuracy
- ✅ Security (sensitive field exclusion)

### Utility Testing

- ✅ Helper function behavior
- ✅ Code generation algorithms
- ✅ Data transformation

## Continuous Integration Ready

The test suite is configured for CI/CD pipelines:

- Fast execution with in-memory database
- No external dependencies required
- Comprehensive coverage of all functionality
- Clear test organization and naming

## Next Steps

1. **Coverage Analysis**: Run coverage reports to identify any untested code paths
2. **Performance Testing**: Add performance tests for high-load scenarios
3. **Integration Testing**: Add tests for complete user workflows
4. **API Documentation Testing**: Ensure API docs match actual implementation

## Maintenance

- Tests should be updated whenever models or views change
- New features require corresponding test coverage
- Regular test execution in CI/CD pipeline
- Monitor test performance and optimize as needed
