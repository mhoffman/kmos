module btree

    implicit none
    type ::  binary_tree
        real, allocatable, dimension(:) :: rate_constants
        integer, allocatable, dimension(:) :: procs
        integer :: levels, total_length, filled
    end type


contains

    function btree_init(n) result(self)
        type(binary_tree) :: self
        integer, intent(in) :: n


        self%levels = ceiling(log(real(n)) / log(2.) + 1)
        self%total_length = 2 ** self%levels
        allocate(self%rate_constants(self%total_length))
        allocate(self%procs(self%total_length/2))
        self%filled = 0

    end function btree_init


    subroutine btree_destroy(self)
        type(binary_tree),  intent(inout) :: self

        deallocate(self%rate_constants)
        deallocate(self%procs)

    end subroutine btree_destroy


    subroutine btree_repr(self)
        type(binary_tree)  :: self
        integer :: a, b, n

        do n = 0, (self%levels - 1)
        a = 2 ** n
        b = 2 ** (n + 1) - 1
        enddo

    end subroutine btree_repr


    subroutine btree_add(self, rate_constant, proc)
        type(binary_tree) :: self
        real :: rate_constant
        integer :: proc

        integer :: pos

        if(self%filled * 2 + 1 > self%total_length)then
            print *, "btree_add"
            print *, "Tree overfull!!! Quit."
            stop
        endif

        pos = self%total_length / 2 + self%filled
        self%rate_constants(pos) = rate_constant
        call btree_update(self, pos)

        self%filled = self%filled + 1
        self%procs(self%filled) = proc

    end subroutine btree_add


    subroutine btree_del(self, pos)
        type(binary_tree) :: self
        integer, intent(in) :: pos
        integer :: pos_, filled_

        pos_ = pos + self%total_length / 2 
        filled_ = self%filled + self%total_length / 2 

        ! move deleted new data field
        self%rate_constants(pos_) = &
            self%rate_constants(filled_)
        self%rate_constants(filled_) = 0.

        self%procs(pos_) = self%procs(filled_)
        self%procs(filled_) = 0

        ! update tree structure
        call btree_update(self, pos_)
        call btree_update(self, filled_)

        ! decrease tree structure
        self%filled = self%filled - 1

    end subroutine btree_del


    subroutine btree_replace(self, pos, new_rate)
        type(binary_tree) :: self
        real, intent(in) :: new_rate
        integer, intent(in) :: pos

        self%rate_constants(self%total_length/2 + pos) = new_rate
        call btree_update(self, self%total_length/2 + pos)

    end subroutine btree_replace


    subroutine btree_update(self, pos)
        type(binary_tree) :: self
        integer, intent(in) :: pos
        integer :: pos_

        pos_ = pos
        do while (pos_ > 1)
        pos_ = pos_ / 2
        self%rate_constants(pos_) = self%rate_constants(2 * pos_) + self%rate_constants(2 * pos_ + 1)

        end do
    end subroutine btree_update


    subroutine btree_pick(self, x, n)
        type(binary_tree), intent(in) :: self
        real, intent(inout) :: x
        integer, intent(out) :: n


        n = 1
        do while (n < self%total_length / 2)
        if (x < self%rate_constants(n)) then
            n = 2 * n
        else
            x = x - self%rate_constants(n)
            n = 2 * n + 2
        endif
        enddo

        if(x > self%rate_constants(n))then
            n = n + 1
        endif

        n = self%procs(1 + n - self%total_length / 2)

    end subroutine btree_pick

end module btree

program main
    use btree
    implicit none


    type(binary_tree), dimension(:), allocatable :: t
    !type(binary_tree) :: t
    integer :: n, i, a
    real :: x, y, z


    n = 1

    allocate(t(n))
    do i =  1, n
    t(i) = btree_init(80)
    enddo

    do i = 1, 800
    call btree_add(t(1), 1., i)
    enddo
    !call btree_repr(t(1))


    !do i = 1, n 
    !call btree_destroy(t(i))
    !enddo

end program
