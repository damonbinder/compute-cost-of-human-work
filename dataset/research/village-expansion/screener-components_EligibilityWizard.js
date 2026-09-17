import React, { useState } from 'react';
import styled, { css } from 'styled-components';
import { SUPPORTED_COUNTRIES } from '../data/programs';

const steps = [
  { id: 'location', title: 'Location', description: 'Tell us where you live.' },
  {
    id: 'household',
    title: 'Household',
    description: 'Share your household size, age, and dependents.'
  },
  {
    id: 'financial',
    title: 'Income & Work',
    description: 'We use this to match income-based programs.'
  },
  {
    id: 'circumstances',
    title: 'Special Circumstances',
    description: 'Let us know about caregiving or health needs.'
  }
];

const initialFormValues = {
  country: '',
  householdSize: '1',
  monthlyIncome: '',
  employmentStatus: '',
  age: '',
  childrenUnder18: '0',
  specialCircumstances: {
    disability: false,
    pregnancy: false,
    elderlyCare: false
  }
};

function EligibilityWizard({ onComplete }) {
  const [currentStep, setCurrentStep] = useState(0);
  const [formValues, setFormValues] = useState(initialFormValues);
  const [errors, setErrors] = useState({});

  const handleInputChange = (field, value) => {
    setFormValues(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSpecialCircumstanceChange = key => event => {
    const { checked } = event.target;
    setFormValues(prev => ({
      ...prev,
      specialCircumstances: {
        ...prev.specialCircumstances,
        [key]: checked
      }
    }));
  };

  const validateStep = stepId => {
    const newErrors = {};

    if (stepId === 'location') {
      if (!formValues.country) {
        newErrors.country = 'Select your country to continue.';
      }
    }

    if (stepId === 'household') {
      const householdSize = parseInt(formValues.householdSize, 10);
      const children = parseInt(formValues.childrenUnder18, 10);
      const age = Number(formValues.age);

      if (!householdSize || householdSize < 1) {
        newErrors.householdSize = 'Household size must be at least 1.';
      }

      if (Number.isNaN(children) || children < 0) {
        newErrors.childrenUnder18 = 'Enter 0 or more children under 18.';
      } else if (!Number.isNaN(householdSize) && children > householdSize) {
        newErrors.childrenUnder18 = 'Children under 18 cannot exceed household size.';
      }

      if (!age || age < 16) {
        newErrors.age = 'Enter your age (16 or older).';
      }
    }

    if (stepId === 'financial') {
      const monthlyIncome = Number(formValues.monthlyIncome);
      if (formValues.monthlyIncome === '' || Number.isNaN(monthlyIncome) || monthlyIncome < 0) {
        newErrors.monthlyIncome = 'Enter a valid monthly income (0 or higher).';
      }

      if (!formValues.employmentStatus) {
        newErrors.employmentStatus = 'Select your current employment status.';
      }
    }

    return newErrors;
  };

  const prepareSubmission = values => {
    const householdSize = Math.max(parseInt(values.householdSize, 10) || 1, 1);
    const childrenUnder18 = Math.max(parseInt(values.childrenUnder18, 10) || 0, 0);
    const monthlyIncome = Math.max(Number(values.monthlyIncome) || 0, 0);
    const age = Math.max(Number(values.age) || 0, 0);
    const incomePerPerson = monthlyIncome / Math.max(householdSize, 1);

    return {
      country: values.country,
      householdSize,
      monthlyIncome,
      employmentStatus: values.employmentStatus,
      age,
      childrenUnder18,
      incomePerPerson,
      specialCircumstances: values.specialCircumstances
    };
  };

  const handleSubmit = event => {
    event.preventDefault();
    const stepId = steps[currentStep].id;
    const stepErrors = validateStep(stepId);

    if (Object.keys(stepErrors).length > 0) {
      setErrors(stepErrors);
      return;
    }

    setErrors({});

    const isLastStep = currentStep === steps.length - 1;
    if (!isLastStep) {
      setCurrentStep(prev => prev + 1);
      return;
    }

    onComplete(prepareSubmission(formValues));
  };

  const handleBack = () => {
    setErrors({});
    setCurrentStep(prev => Math.max(prev - 1, 0));
  };

  const renderStep = () => {
    switch (steps[currentStep].id) {
      case 'location':
        return (
          <>
            <Field>
              <Label htmlFor="country">Country</Label>
              <Select
                id="country"
                value={formValues.country}
                onChange={event => handleInputChange('country', event.target.value)}
                aria-describedby={errors.country ? 'country-error' : undefined}
              >
                <option value="">Select your location</option>
                {SUPPORTED_COUNTRIES.map(option => (
                  <option key={option.code} value={option.code}>
                    {option.label}
                  </option>
                ))}
              </Select>
              {errors.country && <ErrorMessage id="country-error">{errors.country}</ErrorMessage>}
            </Field>
            <HelperText>
              We currently support federal and national programs in the listed countries.
            </HelperText>
          </>
        );
      case 'household':
        return (
          <>
            <Field>
              <Label htmlFor="householdSize">Household size</Label>
              <NumberInput
                id="householdSize"
                min="1"
                value={formValues.householdSize}
                onChange={event => handleInputChange('householdSize', event.target.value)}
                aria-describedby={errors.householdSize ? 'householdSize-error' : undefined}
              />
              {errors.householdSize && (
                <ErrorMessage id="householdSize-error">{errors.householdSize}</ErrorMessage>
              )}
            </Field>
            <Field>
              <Label htmlFor="age">Your age</Label>
              <NumberInput
                id="age"
                min="16"
                value={formValues.age}
                onChange={event => handleInputChange('age', event.target.value)}
                aria-describedby={errors.age ? 'age-error' : undefined}
              />
              {errors.age && <ErrorMessage id="age-error">{errors.age}</ErrorMessage>}
            </Field>
            <Field>
              <Label htmlFor="childrenUnder18">Children under 18 in your care</Label>
              <NumberInput
                id="childrenUnder18"
                min="0"
                value={formValues.childrenUnder18}
                onChange={event => handleInputChange('childrenUnder18', event.target.value)}
                aria-describedby={errors.childrenUnder18 ? 'childrenUnder18-error' : undefined}
              />
              {errors.childrenUnder18 && (
                <ErrorMessage id="childrenUnder18-error">{errors.childrenUnder18}</ErrorMessage>
              )}
            </Field>
          </>
        );
      case 'financial':
        return (
          <>
            <Field>
              <Label htmlFor="monthlyIncome">Monthly income (local currency)</Label>
              <NumberInput
                id="monthlyIncome"
                min="0"
                value={formValues.monthlyIncome}
                onChange={event => handleInputChange('monthlyIncome', event.target.value)}
                aria-describedby={errors.monthlyIncome ? 'monthlyIncome-error' : undefined}
              />
              {errors.monthlyIncome && (
                <ErrorMessage id="monthlyIncome-error">{errors.monthlyIncome}</ErrorMessage>
              )}
            </Field>
            <Field>
              <Label htmlFor="employmentStatus">Employment status</Label>
              <Select
                id="employmentStatus"
                value={formValues.employmentStatus}
                onChange={event => handleInputChange('employmentStatus', event.target.value)}
                aria-describedby={errors.employmentStatus ? 'employmentStatus-error' : undefined}
              >
                <option value="">Choose an option</option>
                <option value="Employed">Employed (full-time or part-time)</option>
                <option value="Self-employed">Self-employed / informal work</option>
                <option value="Unemployed">Currently unemployed</option>
                <option value="Student">Student</option>
                <option value="Retired">Retired</option>
              </Select>
              {errors.employmentStatus && (
                <ErrorMessage id="employmentStatus-error">{errors.employmentStatus}</ErrorMessage>
              )}
            </Field>
          </>
        );
      case 'circumstances':
        return (
          <>
            <CheckboxGroup role="group" aria-labelledby="special-circumstances-label">
              <CheckboxLabel id="special-circumstances-label">Special circumstances</CheckboxLabel>
              <CheckboxOption>
                <input
                  type="checkbox"
                  id="disability"
                  checked={formValues.specialCircumstances.disability}
                  onChange={handleSpecialCircumstanceChange('disability')}
                />
                <span>Living with a disability</span>
              </CheckboxOption>
              <CheckboxOption>
                <input
                  type="checkbox"
                  id="pregnancy"
                  checked={formValues.specialCircumstances.pregnancy}
                  onChange={handleSpecialCircumstanceChange('pregnancy')}
                />
                <span>Pregnant or postpartum (within the last year)</span>
              </CheckboxOption>
              <CheckboxOption>
                <input
                  type="checkbox"
                  id="elderlyCare"
                  checked={formValues.specialCircumstances.elderlyCare}
                  onChange={handleSpecialCircumstanceChange('elderlyCare')}
                />
                <span>Providing care for an elder (60+)</span>
              </CheckboxOption>
            </CheckboxGroup>
            <HelperText>
              Sharing additional needs helps us surface health, nutrition, and caregiver supports.
            </HelperText>
          </>
        );
      default:
        return null;
    }
  };

  const percentageComplete = ((currentStep + 1) / steps.length) * 100;

  return (
    <WizardCard aria-labelledby="wizard-heading">
      <StepHeader>
        <StepTitle id="wizard-heading">{steps[currentStep].title}</StepTitle>
        <StepDescription>{steps[currentStep].description}</StepDescription>
      </StepHeader>

      <ProgressBar aria-hidden="true">
        <ProgressFill style={{ width: `${percentageComplete}%` }} />
      </ProgressBar>

      <StepIndicator>
        {steps.map((step, index) => {
          const state = index === currentStep ? 'active' : index < currentStep ? 'complete' : 'upcoming';
          return (
            <StepItem key={step.id}>
              <StepCircle data-state={state}>
                <span>{index + 1}</span>
              </StepCircle>
              <small>{step.title}</small>
            </StepItem>
          );
        })}
      </StepIndicator>

      <Form onSubmit={handleSubmit} noValidate>
        <Fieldset>{renderStep()}</Fieldset>
        <ButtonRow>
          {currentStep > 0 && (
            <SecondaryButton type="button" onClick={handleBack}>
              Back
            </SecondaryButton>
          )}
          <PrimaryButton type="submit">
            {currentStep === steps.length - 1 ? 'Check Eligibility' : 'Next'}
          </PrimaryButton>
        </ButtonRow>
      </Form>
    </WizardCard>
  );
}

export default EligibilityWizard;

const WizardCard = styled.section`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const StepHeader = styled.header`
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
`;

const StepTitle = styled.h2`
  font-size: 1.5rem;
  color: ${({ theme }) => theme.colors.primary};
  margin: 0;
`;

const StepDescription = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.muted};
  font-size: 0.95rem;
`;

const ProgressBar = styled.div`
  background: ${({ theme }) => theme.colors.background};
  border-radius: 999px;
  height: 8px;
  width: 100%;
  overflow: hidden;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: linear-gradient(90deg, ${({ theme }) => theme.colors.primary}, ${({ theme }) =>
  theme.colors.secondary});
  transition: width 0.4s ease;
`;

const StepIndicator = styled.ol`
  list-style: none;
  display: flex;
  justify-content: space-between;
  margin: 0;
  padding: 0;
  gap: 0.5rem;
  font-size: 0.8rem;
  text-align: center;
  color: ${({ theme }) => theme.colors.muted};
`;

const StepItem = styled.li`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  min-width: 0;
  small {
    font-weight: 600;
    color: inherit;
  }
`;

const StepCircle = styled.span`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid ${({ theme }) => theme.colors.primary};
  display: grid;
  place-items: center;
  font-weight: 600;
  color: ${({ theme }) => theme.colors.primary};
  background: ${({ theme }) => theme.colors.surface};
  transition: all 0.3s ease;

  &[data-state='complete'] {
    background: ${({ theme }) => theme.colors.primary};
    color: #fff;
  }

  &[data-state='active'] {
    border-color: ${({ theme }) => theme.colors.secondary};
    color: ${({ theme }) => theme.colors.secondary};
  }
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
`;

const Fieldset = styled.fieldset`
  border: 0;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 1rem;
  min-inline-size: 0;
`;

const Field = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
`;

const Label = styled.label`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const HelperText = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.muted};
  font-size: 0.85rem;
`;

const baseInputStyles = css`
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.6);
  padding: 0.75rem 1rem;
  font-size: 1rem;
  outline: none;
  transition: border 0.2s ease, box-shadow 0.2s ease;
  background: #fff;

  &:focus {
    border-color: ${({ theme }) => theme.colors.primary};
    box-shadow: 0 0 0 4px rgba(30, 136, 229, 0.12);
  }
`;

const NumberInput = styled.input.attrs({ type: 'number' })`
  ${baseInputStyles}
  -moz-appearance: textfield;

  &::-webkit-outer-spin-button,
  &::-webkit-inner-spin-button {
    margin: 0;
    -webkit-appearance: none;
  }
`;

const Select = styled.select`
  ${baseInputStyles}
  background-color: #fff;
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const CheckboxLabel = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const CheckboxOption = styled.label`
  display: flex;
  gap: 0.6rem;
  align-items: center;
  font-size: 0.95rem;
  color: ${({ theme }) => theme.colors.text};

  input {
    width: 20px;
    height: 20px;
  }
`;

const ErrorMessage = styled.span`
  color: #d32f2f;
  font-size: 0.85rem;
`;

const ButtonRow = styled.div`
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  flex-wrap: wrap;
`;

const PrimaryButton = styled.button`
  background: linear-gradient(135deg, ${({ theme }) => theme.colors.primary}, ${({ theme }) =>
  theme.colors.secondary});
  color: #fff;
  padding: 0.75rem 1.6rem;
  border: 0;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 20px rgba(30, 136, 229, 0.25);
  }
`;

const SecondaryButton = styled.button`
  background: transparent;
  color: ${({ theme }) => theme.colors.primary};
  border: 1px solid rgba(30, 136, 229, 0.4);
  padding: 0.75rem 1.5rem;
  border-radius: 999px;
  font-weight: 600;
  cursor: pointer;
  transition: border 0.2s ease, color 0.2s ease;

  &:hover {
    border-color: ${({ theme }) => theme.colors.primary};
    color: ${({ theme }) => theme.colors.secondary};
  }
`;
