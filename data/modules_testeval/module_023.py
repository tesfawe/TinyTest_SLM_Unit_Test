def strongPasswordChecker(password: str) -> int:
    def getMissing(password: str) -> int:
        return (
            3
            - any(c.isupper() for c in password)
            - any(c.islower() for c in password)
            - any(c.isdigit() for c in password)
        )

    n = len(password)
    missing = getMissing(password)
    replaces = 0
    oneSeq = 0
    twoSeq = 0

    i = 2
    while i < n:
        if password[i] == password[i - 1] and password[i - 1] == password[i - 2]:
            length = 2

            while i < n and password[i] == password[i - 1]:
                length += 1
                i += 1

            replaces += length // 3

            if length % 3 == 0:
                oneSeq += 1

            if length % 3 == 1:
                twoSeq += 1
        else:
            i += 1

    if n < 6:
        return max(6 - n, missing)

    if n <= 20:
        return max(replaces, missing)

    deletes = n - 20

    replaces -= min(oneSeq, deletes)
    replaces -= min(max(deletes - oneSeq, 0), twoSeq * 2) // 2
    replaces -= max(deletes - oneSeq - twoSeq * 2, 0) // 3

    return deletes + max(replaces, missing)