import logging
from Crypto.Util.number import getStrongPrime
from random import randint, sample
from GET_KEY import get_key_by_eq, get_key_by_lagrange_interpolation

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
logger = logging.getLogger("Shamir Protocol")

BIT_SIZE = 512
T = 6
N = 12


def create_users(N):
    users = list()
    for _ in range(N):
        users.append(ShamirUser(T, N))
    return users


def set_user_points(users, dealer) -> None:
    for index, user in enumerate(users):
        point = dealer.get_point(index)
        user.set_point(point)


def set_params(dealer, users) -> None:
    dealer.set_coefficients()
    dealer.set_values()
    for i, user in enumerate(users):
        point = dealer.get_value(i)
        user.set_value(point)


def restore_keys(users, dealer, T):
    def print_results(resp):
        if resp:
            logger.info("Key assembly completed successfully")
            logger.info(f"Received key: {result}")
            logger.info(f"Generated by dealer key: {dealer.get_key()}")
        else:
            logger.info("The resulting key is different from the generated one")
            logger.info(f"Received key: {result}")
            logger.info(f"Generated by dealer key: {dealer.get_key()}")
    users_for_verify = sample(users, T)
    logger.info("SOLVING EQUATIONS")
    result = get_key_by_eq(users_for_verify, dealer.P)
    if result:
        print_results(result == dealer.get_key())
    logger.info("LAGRANGE INTERPOLATION")
    result = get_key_by_lagrange_interpolation(users_for_verify, dealer.P)
    print_results(result == dealer.get_key())


def key_sharing():
    dealer = ShamirDealer(T, N)
    users = create_users(N)
    dealer.set_points()
    set_user_points(users, dealer)
    set_params(dealer, users)
    restore_keys(users, dealer, T)
    logger.info("-" * 100)
    restore_keys(users, dealer, T - 1)


class ShamirDealer:

    P = getStrongPrime(BIT_SIZE)

    def __init__(self, t, n):
        self._t = t
        self._n = n
        self._points = list()
        self._coefficients = list()
        self._values = list()
        self._key = None

    def set_points(self):
        for point in range(1, self._n + 1):
            self._points.append(point)

    def get_points(self):
        return self._points

    def get_point(self, index):
        return self._points[index]

    def get_random_element(self):
        return randint(2, self.P - 2)

    def set_key(self):
        self._key = self.get_random_element()

    def get_key(self):
        return self._key

    def get_value(self, index):
        return self._values[index]

    def set_coefficients(self):
        self.set_key()
        self._coefficients.append(self._key)
        for _ in range(self._t - 1):
            self._coefficients.append(self.get_random_element())

    def set_values(self):
        for point in self._points:
            prev = list()
            for power, coefficient in enumerate(self._coefficients):
                prev.append(coefficient * (point ** power))
            self._values.append(sum(prev) % self.P)


class ShamirUser:
    def __init__(self, t, n):
        self._n = n
        self._t = t
        self._point = None
        self._value = None

    def set_point(self, point):
        self._point = point

    def set_value(self, value):
        self._value = value

    def get_value(self):
        return self._value

    def get_point(self):
        return self._point

    def get_eq(self):
        eq = [1]
        for power in range(1, self._t):
            eq.append(self._point ** power)
        return eq, [self._value]


if __name__ == "__main__":
    key_sharing()
