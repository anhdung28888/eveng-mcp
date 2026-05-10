# Build And Integration Test Plan

## Muc tieu

Muc tieu la dua du an ve trang thai:

- Build package thanh cong va lap lai duoc.
- Chi giu lai va van hanh nhom integration test.
- Loai bo hoac tach rieng unit test, e2e script thu cong, va legacy script khoi pipeline chinh.
- Tao duoc mot quy trinh chay integration test ro rang tren may local va trong CI.

## Hien trang da xac minh

### 1. Build

- `uv build` dang chay thanh cong.
- `pyproject.toml` yeu cau Python `>=3.11`.
- May hien tai mac dinh dang tro vao Python `3.10.11`, nhung `uv run` da dung duoc Python `3.11.7`.

### 2. Test infrastructure

- `pytest` duoc cau hinh trong `pyproject.toml` voi `testpaths = ["tests"]`.
- Repo co nhieu nhom test: `unit`, `integration`, `e2e`, `legacy`.
- Tai lieu test hien khong dong bo voi repo thuc te.

### 3. Blocker hien tai

- `tests/conftest.py` import API cu `eveng_mcp_server.client`, trong khi code hien tai su dung wrapper trong `eveng_mcp_server.core`.
- `eveng_mcp_server.config.settings` khoi tao config global ngay luc import; bien moi truong `DEBUG` hien co gia tri khong hop le lam pytest vo ngay o buoc collect.
- `tests/run_tests.py` tham chieu toi file khong ton tai va co duong dan script sai.
- Mot so integration test hien la script thu cong, phu thuoc MCP Inspector, HTTP endpoint, hoac shell command, nhung chua duoc to chuc thanh integration suite on dinh.
- Mot so tai lieu va script van goi CLI command khong ton tai nhu `list-labs`, `create-lab`, `get-lab-details`.

## Pham vi moi

Chi giu lai integration test. Cu the:

- Giu `tests/integration/` lam test suite chinh.
- Khong dua `tests/unit/` vao muc tieu xanh.
- Khong dua `tests/e2e/` vao pipeline chinh o giai doan nay.
- `tests/legacy/` duoc xem la tai san tham khao, khong thuoc test gate.

## Nguyen tac thuc hien

1. Khong sua de "lua" test xanh; test phai phan anh dung giao dien va hanh vi hien tai.
2. Test nao can EVE-NG that phai duoc gan marker/skip ro rang.
3. Integration suite phai co the chay trong 2 che do:
   - Khong co EVE-NG: collect thanh cong, test lien quan duoc skip hop le.
   - Co EVE-NG + cau hinh day du: test chay that va co assertion ro rang.
4. Moi tai lieu huong dan chay test phai khop voi command thuc te.

## Ke hoach chi tiet

### Giai doan 1: Chot baseline build va runtime

Muc tieu:

- Co mot cach build va run duy nhat bang `uv`.
- Chot Python 3.11 la runtime chuan.

Cong viec:

- Xac nhan lai `pyproject.toml`, `uv.lock`, entrypoint package, va command build.
- Chuan hoa lenh local:
  - `uv build`
  - `uv sync --extra test` hoac `uv sync --dev` tuy theo phu thuoc thuc te can cho integration suite
- Ghi ro yeu cau Python 3.11 trong tai lieu.

Dieu kien hoan thanh:

- Build luon thanh cong bang `uv build`.
- Moi lenh test deu chay qua `uv run ...`, khong phu thuoc Python 3.10 he thong.

### Giai doan 2: Lam sach pytest collection cho integration scope

Muc tieu:

- `pytest --collect-only` khong bi vo vi import side effects.

Cong viec:

- Sua `eveng_mcp_server.config.settings` de khong fail ngay khi import do bien moi truong khong hop le.
- Giam import side effect trong `eveng_mcp_server.__init__` neu can.
- Chinh `tests/conftest.py` theo API hien tai cua du an.
- Cau hinh pytest de chi collect `tests/integration/` cho pipeline integration.

Lua chon ky thuat uu tien:

- Hoac sua `pyproject.toml`/command runner de chi target `tests/integration`.
- Hoac tach `conftest.py` chung thanh `tests/integration/conftest.py` rieng, tranh de phan unit-test cu lam vo collection.

Dieu kien hoan thanh:

- `uv run python -m pytest tests/integration --collect-only` chay duoc.

### Giai doan 3: Kiem ke va phan loai lai integration test that su

Muc tieu:

- Biet chinh xac test nao la integration test hop le, test nao la script thu cong.

Cong viec:

- Rasoat toan bo file trong `tests/integration/`.
- Tach thanh 3 nhom:
  - Automated integration tests co the dua vao pytest.
  - Semi-automated tests can MCP Inspector / server process.
  - Manual scripts chi dung de debug.
- Doi ten, di chuyen, hoac reclassify cac file de phan loai ro rang.

Ky vong ket qua:

- Chi giu lai trong `tests/integration/` cac test co assertion may moc va duoc pytest quan ly.
- Script debug thu cong chuyen sang thu muc phu, vi du `tests/manual/` hoac `tests/integration/manual/`.

### Giai doan 4: Dong bo test voi public API hien tai

Muc tieu:

- Integration test phai test dung giao dien dang ton tai cua du an.

Cong viec:

- Doi import API cu sang API hien tai trong `eveng_mcp_server.core`, `eveng_mcp_server.server`, `eveng_mcp_server.cli`.
- Neu can tuong thich nguoc de giam chi phi sua test, tao shim nho cho import path cu. Chi lam neu loi ich ro rang.
- Sua cac command trong script/test de dung voi CLI co that.

Diem can xu ly:

- Hien CLI chi co `run`, `test-connection`, `config-info`, `version`.
- Cac script dang goi `list-labs`, `create-lab`, `get-lab-details` phai duoc viet lai theo MCP Inspector hoac loai khoi integration suite.

Dieu kien hoan thanh:

- Khong con import path cu trong integration suite chinh.
- Khong con command CLI "ao" trong workflow test chinh.

### Giai doan 5: Thiet ke lai integration suite theo cap

Muc tieu:

- Co integration suite nho, on dinh, de mo rong dan.

De xuat chia thanh 3 cap:

#### Cap A: Server startup va MCP surface

Test cac ca sau:

- Khoi dong server o `stdio` thanh cong.
- Khoi dong server o `sse` thanh cong.
- `tools/list` tra ve danh sach tool.
- `resources/list` tra ve resources.
- `prompts/list` tra ve prompts.

Yeu cau:

- Khong can EVE-NG that.
- Neu EVE-NG khong san sang, server van startup duoc va test surface van chay.

#### Cap B: Integration voi process/transport

Test cac ca sau:

- Giao tiep qua MCP Inspector CLI hoac client stdio Python.
- Giao tiep qua HTTP/SSE endpoint neu du an ho tro.
- Xac nhan JSON-RPC flow `initialize`, `tools/list`, `tools/call` hoat dong.

Yeu cau:

- Tu dong spawn server trong fixture.
- Assertion dua tren response thay vi `print`.

#### Cap C: Live EVE-NG integration

Test cac ca sau:

- `connect_eveng_server`
- `test_connection`
- `get_server_info`
- Mot workflow nho nhat voi lab, chi khi co moi truong that.

Yeu cau:

- Dung env/option ro rang: host, username, password, port, protocol.
- Test phai co cleanup tai nguyen.
- Test phai skip neu khong co EVE-NG config.

### Giai doan 6: Viet lai fixture va runner cho integration

Muc tieu:

- Moi nguoi chi can mot lenh de chay integration tests.

Cong viec:

- Tao `tests/integration/conftest.py` rieng.
- Tao fixture cho:
  - spawn MCP server
  - tao client stdio/SSE
  - nap test config tu env
  - live EVE-NG skip logic
- Rut gon hoac viet lai `tests/run_tests.py` thanh runner danh rieng cho integration.

De xuat command chuan:

- `uv run python -m pytest tests/integration -q`
- `uv run python -m pytest tests/integration -m \"not live_eveng\" -q`
- `uv run python -m pytest tests/integration -m live_eveng -q`

Dieu kien hoan thanh:

- Co mot command local chay duoc integration suite co skip hop le.

### Giai doan 7: Loai bo hoac tach rieng cac thanh phan gay nhieu nhieu

Muc tieu:

- Pipeline chinh khong bi anh huong boi script debug va tai lieu cu.

Cong viec:

- Loai `tests/unit/` khoi test command mac dinh.
- Loai `tests/e2e/` khoi integration pipeline.
- Di chuyen `tests/legacy/` va cac script debug thu cong sang khu vuc phi-chinh.
- Danh dau ro file nao la "manual verification only".

Dieu kien hoan thanh:

- Integration suite chinh khong phu thuoc file legacy/e2e/unit.

### Giai doan 8: Dong bo tai lieu

Muc tieu:

- Tai lieu phai huong dan dung quy trinh moi.

Cong viec:

- Sua `README.md`, `docs/README.md`, `tests/README.md`.
- Cap nhat:
  - Python version
  - lenh cai dependency
  - lenh build
  - lenh chay integration tests
  - yeu cau EVE-NG that va skip behavior
- Loai bo command CLI khong ton tai.

Dieu kien hoan thanh:

- Nguoi moi vao repo co the build va chay integration test theo tai lieu ma khong gap lenh sai.

## Thu tu thuc hien de xuat

1. Chot Python 3.11 + `uv` lam runtime duy nhat.
2. Sua config/import side effects de pytest collect duoc.
3. Co lap `tests/integration/` khoi cac nhom test khac.
4. Rasoat va phan loai lai cac file integration.
5. Viet lai fixture + runner integration.
6. Chinh sua tung integration test theo API/CLI hien tai.
7. Chay xanh integration suite o che do khong co EVE-NG.
8. Chay xanh nhom live EVE-NG khi co moi truong.
9. Cap nhat tai lieu.

## Dinh nghia hoan thanh

Ke hoach nay duoc xem la hoan thanh khi dat du cac dieu kien sau:

- `uv build` xanh.
- `uv run python -m pytest tests/integration --collect-only` xanh.
- Integration suite co the chay tren may khong co EVE-NG va skip hop le.
- Integration suite live EVE-NG chay xanh khi cung cap du env/config.
- Khong con unit/e2e/legacy nam trong pipeline chinh.
- Tai lieu build va integration test da duoc cap nhat khop voi code thuc te.

## Rui ro chinh

- API test va code hien tai lech nhau kha nhieu, co the phai viet lai phan lon integration test.
- MCP Inspector CLI co the gay flaky tren Windows neu dung subprocess khong on dinh.
- Live EVE-NG test co nguy co de lai tai nguyen neu cleanup khong chat.
- Tai lieu hien sai nhieu diem, nen neu khong sua dong bo se tiep tuc gay nham khi van hanh.

## Dau ra mong doi sau khi thuc hien

- Mot quy trinh build on dinh bang `uv`.
- Mot integration suite nho gon, phan lop ro rang, assertion that, co skip logic dung.
- Mot runner va tai lieu de bat ky ai trong nhom cung lap lai duoc ket qua.

## Tong ket thuc thi

Phan nay tom tat cac cong viec da hoan thanh tuong ung voi tung giai doan trong ke hoach ban dau.

### Giai doan 1: Chot baseline build va runtime

Da thuc hien:

- Xac nhan build package bang `uv build` va giu `uv` lam duong build chinh.
- Cai phu thuoc test bang `uv sync --extra test`.
- Chot Python 3.11 cho test runner va cap nhat tai lieu theo huong do.
- Trong qua trinh van hanh, doi test harness sang goi truc tiep `.venv\Scripts\python.exe` thay vi phu thuoc `uv run` o moi buoc, de tranh lock file launcher tren Windows.

Ket qua:

- Build xanh on dinh.
- Test suite chay bang Python 3.11 trong `.venv`.

### Giai doan 2: Lam sach pytest collection cho integration scope

Da thuc hien:

- Sua `eveng_mcp_server.config.settings` de chap nhan cac gia tri moi truong pho bien nhu `release` cho `DEBUG` thay vi vo ngay luc import.
- Thay `tests/conftest.py` cu bang ban moi tap trung cho integration suite.
- Them marker va fixture phu hop cho `live_eveng`, `stdio`, `sse`.
- Dam bao `pytest --collect-only` chi con collect cac test integration duoc duy tri.

Ket qua:

- `tests/integration` collect thanh cong.
- Khong con blocker do import path cu hay environment side effect.

### Giai doan 3: Kiem ke va phan loai lai integration test that su

Da thuc hien:

- Rasoat lai toan bo `tests/integration`.
- Xac dinh cac file `run_mcp_tests.sh`, `test_lab_integration.sh`, `direct_api_test.py`, `working_demo.py` la tai san tham khao/debug, khong dua vao automated gate.
- Giu lai trong automated gate cac bai test pytest duoc viet lai co assertion that.

Ket qua:

- Integration suite duoc thu hep ve nhung bai test co the chay tu dong va lap lai duoc.

### Giai doan 4: Dong bo test voi public API hien tai

Da thuc hien:

- Viet lai integration tests de dung giao dien hien tai cua CLI va MCP server.
- Bo cac command CLI khong ton tai nhu `list-labs`, `create-lab`, `get-lab-details` khoi workflow test chinh.
- Chuyen sang dung MCP Python client chinh thuc cho `stdio` va `sse` thay vi dua vao `npx inspector` hoac `socat`.
- Sua logic ung dung o `lab_management` va `eveng_client` de phu hop response that tu EVE-NG:
  - bo sung `delete_lab` dung tren wrapper
  - sua `get_lab_details` de xu ly dung shape du lieu `nodes`, `networks`, `links`

Ket qua:

- Integration tests dang test dung API/CLI hien tai cua du an.
- Live workflow tao/xem/xoa lab chay thanh cong tren EVE-NG that.

### Giai doan 5: Thiet ke lai integration suite theo cap

Da thuc hien:

- Trien khai nhom test surface cho `stdio`:
  - list tools
  - list resources
  - list prompts
- Trien khai nhom test surface cho `sse`.
- Trien khai nhom live EVE-NG cho:
  - `connect_eveng_server`
  - `test_connection`
  - `create_lab`
  - `list_labs`
  - `get_lab_details`
  - `delete_lab`
- Trien khai nhom CLI integration cho:
  - `version`
  - `config-info`
  - `test-connection`

Ket qua:

- Suite co phan lop ro rang giua non-live va live integration.

### Giai doan 6: Viet lai fixture va runner cho integration

Da thuc hien:

- Tao fixture chung trong `tests/conftest.py` cho:
  - env config
  - live EVE-NG skip logic
  - spawn server SSE
  - chuan hoa interpreter dung cho subprocess
- Viet lai `tests/run_tests.py` thanh runner gon chi phuc vu integration suite.
- Them huong chay collect-only, non-live, live tu runner.

Ket qua:

- Co quy trinh van hanh ro rang de chay integration suite.

### Giai doan 7: Loai bo hoac tach rieng cac thanh phan gay nhieu nhieu

Da thuc hien:

- Loai `unit`, `e2e`, `legacy` khoi automated gate.
- Khong xoa cac script tham khao, nhung tai lieu da noi ro chung khong nam trong test gate.
- Tach hoan toan workflow maintained ra khoi cac script debug cu.

Ket qua:

- Pipeline chinh chi tap trung vao integration tests duoc duy tri.

### Giai doan 8: Dong bo tai lieu

Da thuc hien:

- Cap nhat `README.md`, `docs/README.md`, `tests/README.md`.
- Dong bo:
  - yeu cau Python 3.11
  - cach cai dependency test
  - lenh build
  - lenh collect integration
  - lenh chay non-live va live integration
  - cach truyen thong tin EVE-NG that
- Cap nhat marker trong `pyproject.toml`.

Ket qua:

- Tai lieu da khop voi quy trinh build va integration test hien tai.

## Ket qua xac thuc cuoi cung

Da chay thanh cong:

- `uv build`
- `.venv\Scripts\python.exe -m pytest tests/integration --collect-only -q`
- `.venv\Scripts\python.exe -m pytest tests/integration -m "not live_eveng" -q`
- `.venv\Scripts\python.exe -m pytest tests/integration -m live_eveng -q --eveng-host 192.168.168.141 --eveng-user admin --eveng-pass eve --eveng-port 80 --eveng-protocol http`

Ket qua:

- Non-live integration: `4 passed`
- Live integration: `2 passed`
- Build: thanh cong, tao duoc wheel va sdist
