import enum
import os
from pathlib import Path
import shutil
import subprocess
import threading
from typing import Optional, Tuple

MUX = threading.Semaphore()

class _K6Env:
    INFLUX_HOST: str = os.environ.get('INFLUX_HOST', 'localhost')
    INFLUX_ORG: str = os.environ.get('INFLUX_ORG', 'myorg')
    INFLUX_BUCKET: str = os.environ.get('INFLUX_BUCKET', 'bucket')
    INFLUX_TOKEN: str = os.environ.get('INFLUX_TOKEN', 'my-very-secret-token')
    INFLUX_INSECURE: str = os.environ.get('INFLUX_INSECURE', 'false')

    LT_URL: str = os.environ.get('LT_URL', 'http://localhost/')
    LT_VUS: int = int(os.environ.get('LT_VUS', '10'))
    LT_ITERATIONS: int = int(os.environ.get('LT_ITERATIONS', '10'))
    BASE_URL: str = os.environ.get('BASE_URL', 'localhost:8084')
    TX_PROTO: str = os.environ.get('TX_PROTO', 'http')

    ES6_DIR: Path = Path('/workdir')


class ReturnStatus(enum.Enum):
    STARTED = 0
    FAILURE = 1
    NO_ACTION = 2


class _StatusMuxer:

    def __init__(self):
        self._mux = threading.Semaphore()
        self._running: bool = False
        self._last_status: Optional[int] = None
        self._last_error_msg: Optional[str] = None
        self._last_success_msg: Optional[str] = None

    @property
    def running(self) -> bool:
        ''' Process is currently running. '''
        with self._mux:
            value = self._running
        return value

    @property
    def status_code(self) -> Optional[int]:
        ''' If process completed, the status code returned. '''
        with self._mux:
            value = self._last_status
        return value

    @property
    def msg(self) -> Optional[str]:
        ''' Sucess message if return was successful. '''
        with self._mux:
            value = self._last_success_msg
        return value

    @property
    def error_msg(self) -> Optional[str]:
        ''' Error message if return was not successful. '''
        with self._mux:
            value = self._last_error_msg
        return value

    def start(self):
        ''' Set everything to indicate the process as started. '''
        with self._mux:
            if self._running:
                return False
            self._running = True
            self._last_status = None
            self._last_error_msg = None
            self._last_success_msg = None
            return True

    def error(self, code: int, msg: bytes) -> bool:
        ''' Set error code and message and set to not running. '''
        with self._mux:
            if not self._running:
                return False
            self._running = False
            self._last_status = code
            try:
                self._last_error_msg = msg.decode()
            except UnicodeDecodeError:
                self._last_error_msg = f'{msg}'
            return True

    def success(self, msg: bytes) -> bool:
        ''' Set success code and message and set to not running. '''
        with self._mux:
            if not self._running:
                return False
            self._running = False
            self._last_status = 0
            try:
                self._last_success_msg = msg.decode()
            except UnicodeDecodeError:
                self._last_success_msg = f'{msg}'
            return True


_STAT = _StatusMuxer()


def _run_tests_thr(script: bytes):
    _STAT.start()

    try:
        build_path = Path('build')
        shutil.rmtree(build_path, ignore_errors=True)

        script_path = Path('main.js')
        script_path.write_bytes(script)

        env = {
            **os.environ,
            'BASE_URL': _K6Env.BASE_URL,
            'TX_PROTO': _K6Env.TX_PROTO,
        }
        cmd = 'npm run-script webpack'.split()
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        if proc.returncode != 0:
            return _STAT.error(proc.returncode, proc.stdout)

        cmd = [
            'k6',
            'run',
            *(['-o', f'xk6-influxdb={_K6Env.INFLUX_HOST}'] if _K6Env.INFLUX_HOST else []),
            'build/app.bundle.js',
            # 'main.mjs',
        ]
        env = {
            **os.environ,
            'BASE_URL': "${BASE_URL:-localhost:8084}",
            'TX_PROTO': "${TX_PROTO:-http}",
        }
        if _K6Env.INFLUX_HOST:
            env.update({
                'K6_INFLUXDB_ORGANIZATION': _K6Env.INFLUX_ORG,
                'K6_INFLUXDB_BUCKET': _K6Env.INFLUX_BUCKET,
                'K6_INFLUXDB_TOKEN': _K6Env.INFLUX_TOKEN,
                'K6_INFLUXDB_INSECURE': _K6Env.INFLUX_INSECURE,
            })
        proc = subprocess.run(
            cmd,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        if proc.returncode != 0:
            return _STAT.error(proc.returncode, proc.stdout)

        return _STAT.success(proc.stdout)
    except Exception as _e:  # pylint: disable=broad-except
        _STAT.error(1, f'{_e}'.encode())


def run_k6(script: bytes):
    if _STAT.running:
        return ReturnStatus.NO_ACTION
    thr = threading.Thread(
        target=_run_tests_thr,
        name='load_tester_thr',
        args=(script,),
    )
    thr.start()
    return ReturnStatus.STARTED


def get_status() -> Tuple[str, int]:
    '''
    :returns:   Tuple of (message, status code).
    '''
    def _get_msg(val: Optional[str]) -> str:
        return val if val is not None else ''
    code = _STAT.status_code
    if code is None:
        return 'In progress', 202
    if code == 0:
        return _get_msg(_STAT.msg), 200
    return _get_msg(_STAT.error_msg), 500
