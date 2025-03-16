# GitHub-based Trial Reset Feature

## Changes
- Added new GitHub-based trial reset functionality
- Improved code organization by separating GitHub reset logic into its own module
- Enhanced authentication data extraction and handling
- Added secure credential storage using keyring
- Improved error handling and user feedback
- Added automatic re-login after trial reset
- Integrated JavaScript trial reset code for automatic account deletion

## New Features
- GitHub authentication integration
- Secure credential management
- Automated trial reset process
- Session persistence
- Improved user experience with clear status messages
- Automatic account deletion when usage limit is reached

## Technical Details
- Uses DrissionPage for browser automation
- Implements secure credential storage with keyring
- Handles both cookie and localStorage token formats
- Supports automatic re-login after reset
- Maintains session persistence across resets
- JavaScript trial reset code:
```javascript
function deleteAccount() {
    return new Promise((resolve, reject) => {
        fetch('https://www.cursor.com/api/dashboard/delete-account', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'
        })
        .then(response => {
            if (response.status === 200) {
                resolve('Account deleted successfully');
            } else {
                reject('Failed to delete account: ' + response.status);
            }
        })
        .catch(error => {
            reject('Error: ' + error);
        });
    });
}
```

## Testing
- Tested on Windows 10, macOS, and Linux
- Verified with multiple GitHub accounts
- Confirmed successful trial reset and re-login
- Validated credential storage and retrieval
- Tested automatic account deletion when usage limit is reached
- Verified successful re-authentication after account deletion 