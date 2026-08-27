import type { ReactNode } from 'react';
import type { LoginResponse, Membership, Organization, User } from './api';

export type { User as PlatformUser } from './api';
export type { Membership, Organization } from './api';

export type Impersonation = {
  actorEmail?: string;
  targetEmail?: string;
  targetName?: string;
} | null;

export type AuthContextValue = {
  user: User | null;
  loading: boolean;
  impersonation: Impersonation;
  login: (
    email: string,
    password: string,
  ) => Promise<{ mfaRequired?: boolean; mfaToken?: string; mfaSetupRequired?: boolean }>;
  verifyMfaLogin: (mfaToken: string, code: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  startImpersonation: (orgId: string | number, userId: string | number) => Promise<LoginResponse>;
  exitImpersonation: () => Promise<LoginResponse>;
  hasRole: (...roles: string[]) => boolean;
  isPlatformAdmin: () => boolean;
  isSuperAdmin: () => boolean;
};

export type OrganizationContextValue = {
  organization: Organization | null;
  membership: Membership | null;
  loading: boolean;
  refresh: () => Promise<{ organization: Organization; membership: Membership | null } | undefined>;
  isOrgAdmin: boolean;
  isOrgContentManager: boolean;
  isOrgModerator: boolean;
};

export type PropsWithChildren = {
  children?: ReactNode;
};
