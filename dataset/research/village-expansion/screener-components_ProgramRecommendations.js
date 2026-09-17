import React from 'react';
import styled from 'styled-components';
import { SUPPORTED_COUNTRIES } from '../data/programs';

const countryNameLookup = SUPPORTED_COUNTRIES.reduce((acc, country) => {
  acc[country.code] = country.label;
  return acc;
}, {});

function ProgramRecommendations({ programs, formData }) {
  if (!formData) {
    return (
      <RecommendationsCard aria-live="polite">
        <EmptyStateTitle>See tailored programs here</EmptyStateTitle>
        <EmptyStateText>
          Complete the questions to view financial assistance programs and next steps for your
          household.
        </EmptyStateText>
      </RecommendationsCard>
    );
  }

  const countryLabel = countryNameLookup[formData.country] || formData.country;
  const formattedIncome = new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 0
  }).format(formData.monthlyIncome);
  const formattedIncomePerPerson = new Intl.NumberFormat(undefined, {
    maximumFractionDigits: 0
  }).format(Math.round(formData.incomePerPerson));

  return (
    <RecommendationsCard aria-live="polite">
      <Summary>
        <SummaryTitle>Eligibility Summary</SummaryTitle>
        <SummaryRow>
          <SummaryLabel>Country</SummaryLabel>
          <SummaryValue>{countryLabel || '—'}</SummaryValue>
        </SummaryRow>
        <SummaryRow>
          <SummaryLabel>Household size</SummaryLabel>
          <SummaryValue>{formData.householdSize}</SummaryValue>
        </SummaryRow>
        <SummaryRow>
          <SummaryLabel>Monthly income</SummaryLabel>
          <SummaryValue>
            {formattedIncome} <SummaryHint>(~{formattedIncomePerPerson} per person)</SummaryHint>
          </SummaryValue>
        </SummaryRow>
        <SummaryRow>
          <SummaryLabel>Employment</SummaryLabel>
          <SummaryValue>{formData.employmentStatus || '—'}</SummaryValue>
        </SummaryRow>
      </Summary>

      {programs.length === 0 ? (
        <EmptyState>
          <EmptyStateTitle>No programs matched yet</EmptyStateTitle>
          <EmptyStateText>
            Try adjusting household details or connect with your local social services agency for
            additional assistance options. We continually update program rules.
          </EmptyStateText>
        </EmptyState>
      ) : (
        <ProgramList>
          {programs.map(program => (
            <ProgramCard key={program.id}>
              <ProgramHeader>
                <ProgramName>{program.name}</ProgramName>
                <ProgramCountry>{countryNameLookup[program.country] || program.country}</ProgramCountry>
              </ProgramHeader>
              <ProgramDescription>{program.description}</ProgramDescription>

              <DetailBlock>
                <DetailHeading>Estimated benefit</DetailHeading>
                <DetailText>{program.estimatedBenefit}</DetailText>
              </DetailBlock>

              <DetailBlock>
                <DetailHeading>How to apply</DetailHeading>
                <DetailText>{program.application}</DetailText>
              </DetailBlock>

              {program.nextSteps && program.nextSteps.length > 0 && (
                <DetailBlock>
                  <DetailHeading>Next steps</DetailHeading>
                  <NextStepsList>
                    {program.nextSteps.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </NextStepsList>
                </DetailBlock>
              )}

              <ContactSection>
                {program.phone && (
                  <ContactItem>
                    <ContactLabel>Phone</ContactLabel>
                    <ContactValue>{program.phone}</ContactValue>
                  </ContactItem>
                )}
                {program.website && (
                  <ContactItem>
                    <ContactLabel>Website</ContactLabel>
                    <ContactLink href={program.website} target="_blank" rel="noopener noreferrer">
                      {program.website}
                    </ContactLink>
                  </ContactItem>
                )}
              </ContactSection>
            </ProgramCard>
          ))}
        </ProgramList>
      )}
    </RecommendationsCard>
  );
}

export default ProgramRecommendations;

const RecommendationsCard = styled.section`
  background: ${({ theme }) => theme.colors.surface};
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  min-height: 100%;
`;

const Summary = styled.div`
  border-radius: 16px;
  background: rgba(30, 136, 229, 0.08);
  padding: 1.25rem;
  display: grid;
  gap: 0.8rem;
`;

const SummaryTitle = styled.h3`
  margin: 0;
  color: ${({ theme }) => theme.colors.primary};
  font-size: 1.05rem;
`;

const SummaryRow = styled.div`
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
`;

const SummaryLabel = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.muted};
`;

const SummaryValue = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const SummaryHint = styled.span`
  font-weight: 500;
  color: ${({ theme }) => theme.colors.muted};
  font-size: 0.85rem;
`;

const ProgramList = styled.div`
  display: grid;
  gap: 1.25rem;
`;

const ProgramCard = styled.article`
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 18px;
  padding: 1.5rem;
  display: grid;
  gap: 1rem;
  background: #fff;
  transition: transform 0.2s ease, box-shadow 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 30px rgba(15, 23, 42, 0.12);
  }
`;

const ProgramHeader = styled.header`
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
`;

const ProgramName = styled.h4`
  margin: 0;
  color: ${({ theme }) => theme.colors.text};
  font-size: 1.2rem;
`;

const ProgramCountry = styled.span`
  align-self: flex-start;
  background: rgba(46, 125, 50, 0.12);
  color: ${({ theme }) => theme.colors.secondary};
  border-radius: 999px;
  padding: 0.3rem 0.75rem;
  font-weight: 600;
  font-size: 0.8rem;
`;

const ProgramDescription = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.muted};
  line-height: 1.5;
`;

const DetailBlock = styled.div`
  display: grid;
  gap: 0.4rem;
`;

const DetailHeading = styled.h5`
  margin: 0;
  font-size: 0.95rem;
  color: ${({ theme }) => theme.colors.primary};
  text-transform: uppercase;
  letter-spacing: 0.02em;
`;

const DetailText = styled.p`
  margin: 0;
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.6;
`;

const NextStepsList = styled.ul`
  margin: 0;
  padding-left: 1.2rem;
  display: grid;
  gap: 0.5rem;
  color: ${({ theme }) => theme.colors.text};
  line-height: 1.5;
`;

const ContactSection = styled.div`
  display: grid;
  gap: 0.6rem;
  padding-top: 0.5rem;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
`;

const ContactItem = styled.div`
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
  align-items: center;
`;

const ContactLabel = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.muted};
  min-width: 70px;
`;

const ContactValue = styled.span`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.text};
`;

const ContactLink = styled.a`
  font-weight: 600;
  color: ${({ theme }) => theme.colors.primary};
  text-decoration: underline;
`;

const EmptyState = styled.div`
  border: 1px dashed rgba(30, 136, 229, 0.35);
  border-radius: 16px;
  padding: 1.5rem;
  text-align: left;
  background: rgba(30, 136, 229, 0.04);
`;

const EmptyStateTitle = styled.h4`
  margin: 0;
  color: ${({ theme }) => theme.colors.primary};
`;

const EmptyStateText = styled.p`
  margin: 0.6rem 0 0;
  color: ${({ theme }) => theme.colors.muted};
  line-height: 1.5;
`;
