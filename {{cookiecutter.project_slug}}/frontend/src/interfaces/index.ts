export interface IUserProfile {
    admin_channels: string[];
    admin_roles: string[];
    disabled: boolean;
    email: string;
    full_name: string;
    username: string;
}

export interface IUserProfileUpdate {
    full_name?: string;
    password?: string;
    email?: string;
    admin_channels?: string[];
    admin_roles?: string[];
    disabled?: boolean;
}

export interface IUserProfileCreate {
    username: string;
    full_name?: string;
    password?: string;
    email?: string;
    admin_channels?: string[];
    admin_roles?: string[];
    disabled?: boolean;
}
